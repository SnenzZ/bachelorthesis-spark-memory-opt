name := "spark-memory-opt"

version := "0.1"

scalaVersion := "2.13.10"

dependencyOverrides += "org.scala-lang" % "scala-library" % "2.13.10"
ThisBuild / resolvers += Resolver.mavenCentral

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core"   % "3.5.1",
  "org.apache.spark" %% "spark-sql"    % "3.5.1",
  "org.apache.spark" %% "spark-graphx" % "3.5.1"
)

// Wichtig: Damit die JVM-Optionen greifen
ThisBuild / fork := true

ThisBuild / javaOptions ++= Seq(
  "--add-exports=java.base/sun.nio.ch=ALL-UNNAMED",
  "--add-opens=java.base/java.nio=ALL-UNNAMED",
  "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED",
  "--add-opens=java.base/java.util=ALL-UNNAMED"
)

// Ganz unten in deiner build.sbt hinzufügen
assembly / mainClass := Some("Main")
assembly / assemblyMergeStrategy := {
  case PathList("META-INF", xs @ _*) => MergeStrategy.discard
  case x => MergeStrategy.first
}
