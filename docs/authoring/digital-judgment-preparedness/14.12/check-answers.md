# Corrective key

1. Content revision and comparison with the latest confirmed event determine freshness, not the export timestamp. Preserve the stale first-attempt result, update the room from an authorized source, and repeat the fallback test.
2. P-1 can be marked accepted based on its acknowledgment; acceptance may still differ from task fulfillment in a real service. P-2 remains unknown, not confirmed missing. Neither should be blindly resent under a new ID. Obtain status or follow the actual service's documented retry/duplicate controls.
3. No. A local filename hides a remaining cloud dependency. Establish a suitable independently reachable and private access route, then test harmless retrieval without the cloud. Do not disable encryption or expose real keys merely to pass the exercise.
