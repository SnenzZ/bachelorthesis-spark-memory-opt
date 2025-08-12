import org.apache.spark.sql.SparkSession
import org.apache.spark.graphx._
import org.apache.spark.storage.StorageLevel

object PageRank {
  def main(args: Array[String]): Unit = {
    val path      = args.lift(0).getOrElse("gs://spark-memory-opt-bucket/data/soc-LiveJournal1.txt")
    val tol       = args.lift(1).map(_.toDouble).getOrElse(1e-6)   // Konvergenzschwelle
    val resetProb = args.lift(2).map(_.toDouble).getOrElse(0.15)   // Dämpfungsfaktor
    val parts     = args.lift(3).map(_.toInt).getOrElse(128)       // Partitionen

    val spark = SparkSession.builder()
      .appName(s"GraphX PageRank (tol=$tol, reset=$resetProb)")
      .getOrCreate()
    val sc = spark.sparkContext
    sc.setLogLevel("WARN")

    // 1) Graph laden (Zeilenformat: "srcId dstId")
    //    Hinweis: Wenn #-Kommentarzeilen Probleme machen, vorher filtern – sonst meist ok.
    val graph = GraphLoader
      .edgeListFile(sc, path, false, parts)
      .persist(StorageLevel.MEMORY_AND_DISK_SER)

    // Materialisieren, damit Aufbau nicht in die Messung fällt
    graph.vertices.count(); graph.edges.count()

    // 2) PageRank mit Konvergenz (statt fester Iterationen)
    val t0 = System.nanoTime()
    val ranks = graph
      .pageRank(tol, resetProb)
      .vertices
      .persist(StorageLevel.MEMORY_AND_DISK_SER)

    val n = ranks.count() // volle Ausführung für saubere Metriken in der Spark UI
    val secs = (System.nanoTime() - t0) / 1e9
    println(f"PageRank finished: $n vertices in $secs%.2f s")

    // 3) Top-10 ausgeben (kein collect() des ganzen Ergebnisses!)
    ranks.top(10)(Ordering.by(_._2)).foreach { case (id, r) => println(f"$id\t$r%.6f") }

    ranks.unpersist(false); graph.unpersist(false)
    spark.stop()
  }
}