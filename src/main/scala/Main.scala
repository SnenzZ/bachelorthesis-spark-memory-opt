import org.apache.spark.sql.SparkSession
import org.apache.spark.graphx.{Edge, Graph, VertexId}
import org.apache.spark.storage.StorageLevel
import org.apache.spark.graphx.VertexRDD
import org.apache.spark.graphx.lib.LabelPropagation

object Main {
  type AlgoResult[V] = VertexRDD[V]
  type AlgoFunc[V] = Graph[String, Double] => AlgoResult[V]

  def main(args: Array[String]): Unit = {
    val inputPath = if (args.nonEmpty) args(0) else "data/web-Google.txt"
    // Algorithmus-Name als 2. Argument, z.B. "pagerank", "cc", "triangles"
    val algoName  = if (args.length > 1) args(1).toLowerCase else "pagerank"

    // SparkSession
    val spark = SparkSession.builder()
      .appName(s"GraphX: $algoName")
      .master("local[*]")
      .getOrCreate()
    val sc = spark.sparkContext
    sc.setLogLevel("WARN")

    // Graph aufbauen (wie gehabt)
    val lines = sc.textFile(inputPath)
    val edges = lines
      .filter(l => !l.trim.startsWith("#") && l.nonEmpty)
      .map { l =>
        val Array(src, dst) = l.split("\\s+")
        Edge(src.toLong, dst.toLong, 1.0)
      }
    val vertices = edges.flatMap(e => Seq((e.srcId, e.srcId.toString), (e.dstId, e.dstId.toString)))
      .distinct()
    val defaultV = "unknown"
    val graph = Graph(vertices, edges, defaultV).persist(StorageLevel.MEMORY_ONLY)

    println(s"Graph geladen: ${graph.numVertices} Knoten, ${graph.numEdges} Kanten")

    // Mappe Namen auf Funktion

    val algos: Map[String, AlgoFunc[Double]] = Map(
      "pagerank"  -> (_.staticPageRank(10, resetProb = 0.15).vertices),
      "cc"        -> (_.connectedComponents().vertices.mapValues(_.toDouble)),
      "triangles" -> (_.triangleCount().vertices.mapValues(_.toDouble)),
      "lpa"       -> (g => LabelPropagation.run(g, 5).vertices.mapValues(_.toDouble))
    )

    algos.get(algoName) match {
      case Some(func) =>
        println(s"Starte Algorithmus: $algoName")
        val t0 = System.nanoTime()
        val result = func(graph)
        val duration = (System.nanoTime() - t0) / 1e9
        println(f"$algoName abgeschlossen in $duration%.2f s")

        // Top 10 nach Score
        val top10 = result.join(vertices).map {
          case (_, (value, name)) => (name, value)
        }.sortBy(_._2, ascending = false).take(10)

        println(s"Top 10 Ergebnisse für $algoName:")
        top10.foreach { case (n, v) => println(f"$n: $v%.6f") }

      case None =>
        println(s"Unbekannter Algorithmus '$algoName'. Verfügbare: ${algos.keys.mkString(", ")}")
    }

    //println("\nSpark UI: http://localhost:4040")
    //println("ENTER zum Beenden")
    //scala.io.StdIn.readLine()
    //spark.stop()
  }
}