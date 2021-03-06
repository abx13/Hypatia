# Pingmesh application

The pingmesh application is when you want to continuously sends UDP pings between endpoints to measure their RTT. 

It encompasses the following files:

* `model/apps/udp-rtt-client.cc/h` - Sends out UDP pings and receives replies
* `model/apps/udp-rtt-server.cc/h` - Receives UDP pings, adds a received timestamp, and pings back
* `helper/apps/udp-rtt-helper.cc/h` - Helpers to install UDP RTT servers and clients
* `helper/apps/pingmesh-scheduler.cc/h` - Schedules the pings to start. Once the run is over, it can write the results to file.

You can use the application(s) separately, or make use of the pingmesh scheduler (which is recommended).


## Getting started: pingmesh scheduler

1. Add the following to the `config_ns3.properties` in your run folder (for sending pings between all endpoints at a 100ms granularity):

   ```
   enable_pingmesh_scheduler=true
   pingmesh_interval_ns=100000000
   pingmesh_endpoint_pairs=all
   ```

2. In your code, import the pingmesh scheduler:

   ```
   #include "ns3/pingmesh-scheduler.h"
   ```

3. Before the start of the simulation run, in your code add:

    ```c++
    // Schedule pings
    PingmeshScheduler pingmeshScheduler(basicSimulation, topology); // Requires enable_pingmesh_scheduler=true
    ```
   
4. After the run, in your code add:

    ```c++
    // Write pingmesh results
    pingmeshScheduler.WriteResults();
    ```

5. After the run, you should have the pingmesh log files in the `logs_ns3` of your run folder.


## Getting started: directly installing applications

1. In your code, import the UDP RTT helper:

   ```
   #include "ns3/udp-rtt-helper.h"
   ```
   
2. Before the start of the simulation run, in your code add:

   ```c++
   // Install the reply server on node B: Ptr<Node> node_b
   UdpRttServerHelper echoServerHelper(1025);
   ApplicationContainer app = echoServerHelper.Install(node_b);
   app.Start(Seconds(0.0));
   
   // Install the client on node A: Ptr<Node> node_a
   // There needs a client for each A -> B pair
   int64_t interval_ns = 100000000; // 100 ms
   UdpRttClientHelper source(
        m_nodes.Get(node_b)->GetObject<Ipv4>()->GetAddress(1, 0).GetLocal(),
        1025,
        node_a->GetId(),
        node_b->GetId() 
   );
   source.SetAttribute("Interval", TimeValue(NanoSeconds(interval_ns)));
   ApplicationContainer app_a_to_b = source.Install(node_a);
   app_a_to_b.Start(NanoSeconds(counter * in_between_ns));
   ```

3. After the run, in your code add:

   ```c++
   // Retrieve client
   Ptr<UdpRttClient> client = app_a_to_b->GetObject<UdpRttClient>();

   // Data about this pair
   int64_t from_node_id = client->GetFromNodeId();
   int64_t to_node_id = client->GetToNodeId();
   uint32_t sent = client->GetSent();
   std::vector<int64_t> sendRequestTimestamps = client->GetSendRequestTimestamps();
   std::vector<int64_t> replyTimestamps = client->GetReplyTimestamps();
   std::vector<int64_t> receiveReplyTimestamps = client->GetReceiveReplyTimestamps();
   
   // Now do whatever you want; a timestamp is -1 if it did not arrive (yet)
   ```


## Pingmesh scheduler information

You MUST set the following keys in `config_ns3.properties`:

* `enable_pingmesh_scheduler` : Must be set to `true`
* `pingmesh_interval_ns` : Interval to send a ping (ns)

The following are OPTIONAL:

* `pingmesh_endpoint_pairs` : Endpoint directed pingmesh pairs (either `all` (default) or e.g., `set(0->1, 5->6)` to only have pinging from 0 to 1 and from 5 to 6 (directed pairs))

**The pingmesh log files**

There are two log files generated by the run in the `logs_ns3` folder within the run folder:

* `pingmesh.txt` : Pingmesh results in a human readable table.
* `pingmesh.csv` : Pingmesh results in CSV format for processing with each line:

   ```
   from_node_id,to_node_id,i,send_request_timestamp,reply_timestamp,receive_reply_timestamp,latency_to_there_ns,latency_from_there_ns,rtt_ns,[YES/LOST]
   ```
  
  (with `YES` = ping completed successfully, `LOST` = ping reply did not arrive (either it got lost, or the simulation ended before it could arrive))
