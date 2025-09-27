// file: PRJob.scala
import org.apache.spark.sql.SparkSession
import org.apache.spark.graphx._
import org.apache.spark.graphx.lib.PageRank
import org.apache.spark.rdd.RDD

object PRJob {
  /** Args:
    * 0: inputEdgesPath      (z.B. gs://bucket/data/edges.txt)
    * 1: outputPath          (z.B. gs://bucket/out/pr)
    * 2: numIter             (optional, Int; Default 20)
    * 3: resetProb           (optional, Double in (0,1); Default 0.15)
    * 4: topK                (optional, Int; Default 100 – für CSV)
    */
  def main(args: Array[String]): Unit = {
    require(args.length >= 2,
      "Usage: PRJob <inputEdgesPath> <outputPath> [numIter] [resetProb] [topK]")

    val inputEdgesPath = args(0)
    val outputPath     = args(1)
    val numIter        = if (args.length >= 3) args(2).toInt else 20
    val resetProb      = if (args.length >= 4) args(3).toDouble else 0.15
    val topK           = if (args.length >= 5) args(4).toInt else 100

    val spark = SparkSession.builder()
      .appName("PageRank-GraphX")
      .getOrCreate()
    val sc = spark.sparkContext
    sc.setLogLevel("WARN")

    // --- Kanten einlesen: "srcId dstId" (gerichtet)
    val raw: RDD[String] = sc.textFile(inputEdgesPath)
      .filter(l => l.trim.nonEmpty && !l.trim.startsWith("#"))

    // Kanten als gerichtete Edges
    val edges: RDD[Edge[Int]] = raw.map { line =>
      val parts = line.trim.split("\\s+")
      require(parts.length >= 2, s"Bad edge line: '$line'")
      val src = parts(0).toLong
      val dst = parts(1).toLong
      Edge(src, dst, 1)
    }

    // Alle Knoten aus Edges ableiten (optional separate Vertexliste)
    val vertices: RDD[(VertexId, Int)] = edges.flatMap(e => Iterator(e.srcId, e.dstId))
      .distinct()
      .map(id => (id, 1))

    // Graph erstellen (gerichtet). Optional: Partitionierung für Stabilität
    val g0 = Graph(vertices, edges)
    val graph = g0.partitionBy(PartitionStrategy.EdgePartition2D)

    // --- Compute-Block messen
    val t0 = System.nanoTime()
    // PageRank: fixierte Iterationszahl (für reproduzierbare Runs)
    // Rückgabe: Graph[Double, Double] (Vertex-Attr = Rank, Edge-Attr = Gewicht)
    val prGraph: Graph[Double, Double] = PageRank.run(graph, numIter, resetProb)
    val pr: RDD[(VertexId, Double)] = prGraph.vertices.persist()
    pr.count() // materialisieren
    val computeMs = (System.nanoTime() - t0) / 1e6
    println(f"[METRIC] compute_ms=$computeMs%.2f numIter=$numIter resetProb=$resetProb")

    // --- Ausgabe
    import spark.implicits._
    val prDF = pr.toDF("vertexId", "rank")
    prDF.write.mode("overwrite").parquet(s"$outputPath/parquet")

    // Top-K (nach Rank absteigend) als CSV (bequeme Sicht)
    val topKLocal = pr.sortBy({ case (_, r) => r }, ascending = false).map {
      case (vid, r) => (vid, r)
    }.toDF("vertexId", "rank")

    topKLocal.limit(topK)
      .coalesce(1)
      .write.mode("overwrite")
      .option("header", "true")
      .csv(s"$outputPath/topK_csv")

    // Optional: einfache Summen-/Sanity-Logs
    val nVertices = vertices.count()
    val sumRank = pr.map(_._2).sum()
    println(f"[METRIC] vertices=$nVertices sumRank=$sumRank%.6f")
  }
}
