import statistics

file = open("../sauvegardes/svgde_2022-06-14-2242_1/run_loaded_tm_pairing_5_Mbps_for_240s_with_tcp_algorithm_free_one_only_over_isls/logs_ns3/tcp_flows.txt", "r")

i = 0
duration = list()
avg_rate = list()

for line in file:
    if (i != 0):
        line = line.strip('\n')
        line = line.strip(' ')

        line_list = line.split('\t')
        
        print (line_list)
        print (line_list[6].strip('ms'))
        print (line_list[9].strip('Mbit/s'))

        duration.insert(i-1, line_list[6].strip('ms'))
        avg_rate.insert(i-1, line_list[9].strip('Mbit/s'))
    i+=1
       
file.close()


print("5 Mbps - 240s\n")
print ("Durée Moyenne: "+ statistics.mean(duration)+"\n")
print ("Average Rate Moyenne: "+ statistics.mean(avg_rate)+"\n")


'''
for i in range (len(slope)):
    print (slope[i], " ", distance[i], '\n')
'''