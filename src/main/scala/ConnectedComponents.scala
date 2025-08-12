// file: CCJob.scala
import org.apache.spark.sql.SparkSession
import org.apache.spark.graphx._
import org.apache.spark.graphx.lib.ConnectedComponents
import org.apache.spark.rdd.RDD

object ConnectedComponents {
  /** Args:
    * 0: inputEdgesPath   (z.B. gs://bucket/data/edges.txt)
    * 1: outputPath       (z.B. gs://bucket/out/cc)
    * 2: expectedComponents (optional, Int) – einfache Testprüfung
    */
  def main(args: Array[String]): Unit = {
    require(args.length >= 2,
      "Usage: CCJob <inputEdgesPath> <outputPath> [expectedComponents]")

    val inputEdgesPath = args(0)
    val outputPath     = args(1)
    val expectedOpt    = if (args.length >= 3) Some(args(2).toInt) else None

    val spark = SparkSession.builder()
      .appName("ConnectedComponents-GraphX")
      .getOrCreate()
    val sc = spark.sparkContext
    spark.sparkContext.setLogLevel("WARN")

    // --- Kanten einlesen: Format pro Zeile "srcId dstId"
    //   Beispiel:
    //   1 2
    //   2 3
    //   10 11
    val raw: RDD[String] = sc.textFile(inputEdgesPath)
      .filter(l => l.trim.nonEmpty && !l.trim.startsWith("#"))

    val edges: RDD[Edge[Int]] = raw.map { line =>
      val parts = line.trim.split("\\s+")
      require(parts.length >= 2, s"Bad edge line: '$line'")
      val src = parts(0).toLong
      val dst = parts(1).toLong
      Edge(src, dst, 1)
    }

    // Optional: Alle Knoten sammeln, auch isolierte, falls im Datensatz extra gelistet
    val vertices: RDD[(VertexId, Int)] = edges.flatMap(e => Iterator(e.srcId, e.dstId))
      .distinct()
      .map(id => (id, 1))

    val graph = Graph(vertices, edges)

    // --- Connected Components
    val cc = ConnectedComponents.run(graph).vertices // RDD[(vertexId, componentId)]

    // --- Metriken
    val componentCount = cc.map { case (_, comp) => comp }.distinct().count()
    val componentSizes = cc.map { case (_, comp) => (comp, 1L) }
      .reduceByKey(_ + _)
      .sortBy(_._2, ascending = false)

    // --- Ausgabe (Parquet + CSV der Größen)
    import spark.implicits._
    val ccDF = cc.toDF("vertexId", "componentId")
    ccDF.write.mode("overwrite").parquet(s"$outputPath/parquet")

    val sizesDF = componentSizes.toDF("componentId", "size")
    sizesDF.coalesce(1).write.mode("overwrite").option("header", "true")
      .csv(s"$outputPath/component_sizes_csv")

    // --- Einfache Testprüfung (optional)
    expectedOpt.foreach { exp =>
      if (componentCount != exp) {
        System.err.println(s"[TEST] Expected $exp components, but found $componentCount")
        // Nicht hart abbrechen? -> Für CI/Test sinnvoll mit Exit-Code 1:
        System.exit(1)
      } else {
        println(s"[TEST] OK: componentCount == $exp")
      }
    }

