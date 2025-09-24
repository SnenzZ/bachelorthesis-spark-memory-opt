## Hyoptheses 1 - Serializer
### Run 1 - 4
Die Testergebnisse zeigen eine leichte Verbesserung der GC Time, insbesondere wenn man von Java Serializer auf Kryo Serializer ändert

Mit größeren Datasets ist der Unterschied wahrscheinlich stärker bemerkbar.

Bei SOC haben wir z.B. eine Verbesserung von 3.1 min auf 2.7 min in der Duration (Driver Time).
