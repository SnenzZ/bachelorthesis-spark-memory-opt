name := "spark-memory-opt"
version := "0.1"

scalaVersion := "2.12.18"                 // muss zu Spark 3.5.1 passen

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core"   % "3.5.1" % "provided",
  "org.apache.spark" %% "spark-sql"    % "3.5.1" % "provided",
  "org.apache.spark" %% "spark-graphx" % "3.5.1" % "provided"
)

// optional: nur falls du lokal runnst; für Dataproc nicht nötig
ThisBuild / fork := true
ThisBuild / javaOptions ++= Seq(
  "--add-exports=java.base/sun.nio.ch=ALL-UNNAMED",
  "--add-opens=java.base/java.nio=ALL-UNNAMED",
  "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED",
  "--add-opens=java.base/java.util=ALL-UNNAMED"
)

// --- sbt-assembly Settings ---
import sbtassembly.AssemblyPlugin.autoImport._

assembly / assemblyJarName := "spark-memory-opt-assembly-0.1.jar"
// WICHTIG: keine mainClass festnageln – du nutzt --class beim Submit
Compile / mainClass := None

assembly / assemblyMergeStrategy := {
  case PathList("META-INF", xs @ _*)               => MergeStrategy.discard
  case "module-info.class"                         => MergeStrategy.discard
  case PathList("reference.conf")                  => MergeStrategy.concat
  case PathList("application.conf")                => MergeStrategy.concat
  case PathList("META-INF", "services", xs @ _*)   => MergeStrategy.concat
  case _                                           => MergeStrategy.first
}
