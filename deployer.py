import argparse
import io 
import subprocess
from subprocess import CalledProcessError

''' Script to deploy NoSQL on Docker environment
   This script accepts NoSQL parameters: 
       replication factor
       partitions
    and Docker environment parameters:
      No. of docker containers
      
    1. The script generates a Dockerfile to build an image of Stoarge Node Agent
    2. The script generates a NoSQL script to deploy Storage Node Agents  
       in the specified Topology
       
    Then the script executes the above scripts with one Storage Node Agent
    running in one named Docker container
  
    NoSQL communication requires that the Docker containers are 
    bi-directionally linked.
    While Docker allows to link one container to another, such linking
    is uni-directional.
    
    Bi-directional container linking will require a DNS service.
    
    That is still to be done.
      
'''
parser = argparse.ArgumentParser(description='Deploy NoSQL in Docker')

parser.add_argument("-c", "--container", required=True, type=int, 
    dest="nc", help="no of containers. Must be a non-zero, positive integer")

parser.add_argument("--sna_build_script", default="Dockerfile.sna",
    help="name of a generated Dockerfile for building image of Storage Node Agent (SNA)")

parser.add_argument("--topology_build_script", default="topology_builder.script",
    help= "name of generated script file with commands to build a topology")

parser.add_argument("--kv_version", default="3.4.7",
    help="Version of NoSQL to deploy")

parser.add_argument("--port", type=int, default=5000,
    help='Listen port of NoSQL Stoarge Agent. As each SNA runs in ' +
    'separate Docker container, each SN can listen to the same port number. ' +
    'This is set to 5000, the default port for NoSQL')

parser.add_argument("--admin_port", type=int, default=5001,
    help='Listen port of NoSQL Admin Agent. As each Admin runs in ' +
    'separate Docker container, each Admin can listen to the same port number. ' +
    'This is set to 5001, the default port for NoSQL Admin')

parser.add_argument("--ha_range", default='5010,5020',
    help='HA port range. This range of port are used to inter-group' + 
    ' communication in NoSQL cluster. The group members (replacation' +
    'nodes) run in different Docker containers, the Docker containers' +
    ' must be bi-directionally linked')

parser.add_argument("--capacity", type=int, default=3,
    help='storage node capacity. Determines the maximum number of' +
    'replication nodes managed by a single Storage Node Agent. ' +
    ' The managed nodes are collocated on the same host')

parser.add_argument("--num_cpu", type=int, default=0,
    help='number of CPUs in a Docker container running a Storage Node')

parser.add_argument("--memory_mb", type=int, default=0,
    help='volatile memory available to a Docker container running a Storage Node')

parser.add_argument("--replication_factor", type=int, default=3,
    help='Replication Factor or number of Replication Nodes in a group')

parser.add_argument("--sna_image_name", default="sna",
    help='Docker image name of  a Storage Node Agent')

parser.add_argument("--sn_pool_name", default="allStorageNodes",
    help='Name of Storage Node Pool')

parser.add_argument("--host_prefix", default="host",
    help="Prefix of Docker host names. Actual names are prefix[n]'" + 
    " where n=(0,N]. Defaults to \'host\'")

parser.add_argument("--sn_prefix", default="sn",
    help='Prefix of storage node names. Actual names are prefix[n]' + 
    ' where n=(0,N]. Defaults to \'sn\'')

parser.add_argument("--container_prefix", default="c",
    help='Prefix of Docker container names. Actual names are prefix[n]' + 
    ' where n=(0,N]. Defaults to \'c\'')

parser.add_argument("--zone_name", default="zone",
    help='Name of deployment zone. Defaults to \'zone\'')

parser.add_argument("--store_name", default="cloudStore",
    help='Name of NoSQL store. Defaults to \'cloudStore\'')

parser.add_argument("--topology_name", default="topology",
    help='Name of deployed topology. Defaults to \'topology\'')

parser.add_argument("--partitions", type=int, default=300,
    help='Number of partitions. Defaults to 300')

parser.add_argument('--dry_run', dest='dry_run', action='store_true',
    help="If true, scripts and execution" +
        " commands are generated, but not executed")
parser.add_argument('--run', dest='dry_run', action='store_false')
parser.set_defaults(dry_run=False)

def main(options):
    writeSNAImageBuidScript(options)
    writeTopologyBuildScript(options)
        
    shell_command(options, ['docker', 'build', '--tag', options.sna_image_name, 
        '-f', options.sna_build_script, '.'])
    for i in range(0,options.nc):
        container = options.container_prefix + str(i);
        stop_container(options, container)
        shell_command(options, ["docker", "run",
            "--hostname=" + options.host_prefix+str(i), 
            "--name=" + container,
            "--detach", 
            options.sna_image_name]);
        if (i == 0) :                    
            shell_command(options, ["docker", "cp", options.topology_build_script, 
                  container + ":/" + options.topology_build_script])
    shell_command(options, ["docker", "ps", "--format=\"{{.ID}} {{.Image}} {{.Names}}\""])
   
def writeSNAImageBuidScript(options):
    output =open(options.sna_build_script, 'w')
    
    kv_root = 'kv-' + options.kv_version
    kvstore_jar = kv_root + '/lib/kvstore.jar'
    downloadSite     = 'http://download.oracle.com/otn-pub/otn_software/nosql-database'
    downloadedFile = 'kv-ce-' + options.kv_version + '.zip'
    downloadURL    = downloadSite + '/'  + downloadedFile
    unzipLocation   = kv_root + '/lib'
    
    output.write(u'FROM java' + '\n')
    output.write(u'RUN wget  ' + downloadURL + '\n')
    output.write(u'RUN unzip ' + downloadedFile + ' ' +  unzipLocation+'/*' + '\n');
    output.write(u'RUN rm ' + downloadedFile + '\n');

    output.write(u'RUN mkdir -p ' + kv_root + '\n')
    output.write(u'RUN java -jar ' + kvstore_jar + ' makebootconfig'
        + ' -root  ' + kv_root   
        + ' -port  ' + str(options.port) 
        + ' -admin ' + str(options.admin_port)
        + ' -harange ' + options.ha_range
        + ' -host localhost' 
        + ' -store-security none'
        + ' -capacity '  + str(options.capacity)
        + ' -num_cpus ' + str(options.num_cpu)
        + ' -memory_mb ' + str(options.memory_mb)
        + '\n')

    output.write(u'CMD java -jar ' + kvstore_jar + ' start -root ' + kv_root + '\n')
    
    output.flush()
    output.close()
    
def writeTopologyBuildScript(options): 
    output = open(options.topology_build_script, 'w')
    output.write(u"configure -name " + options.store_name + '\n');
    output.write(u"pool create -name " + options.sn_pool_name + '\n');
    output.write(u"plan deploy-zone -name " + options.zone_name 
        + " -rf " + str(options.replication_factor) + " -wait\n");

    for i in range(0, options.nc) :
        output.write(u"plan deploy-sn -zn " + options.zone_name 
        + " -host " + options.host_prefix + str(i)          
        + " -port " + str(options.port) + " -wait\n");
        
        if (i == 0) :
            output.write(u"plan deploy-admin -sn " + options.sn_prefix + str(i) 
            + " -port " + str(options.admin_port) + " -wait\n");
            output.write(u"pool join -name " + options.sn_pool_name 
                + " -sn " + options.sn_prefix + str(i) + ' -wait\n');
        
        
        output.write(u"topology create -name " + options.topology_name 
            + " -pool " + options.sn_pool_name
            + " -partitions " + str(options.partitions) + " -wait\n");
        output.write(u"plan deploy-topology -name " + options.topology_name + " -wait\n");
    
    output.flush()
    output.close();
    
def shell_command(options, cmds):
    print  '$ %s'  % ' '.join(cmds)
    if options.dry_run:
        return
    else:
        return subprocess.check_call(cmds);    

def stop_container(options, container):
    try:
        shell_command(options, ['docker', 'stop', container])
        shell_command(options, ['docker', 'rm', container])
    except CalledProcessError:
       print 'Can not stop container %s' % container
       
if __name__ == '__main__':
    options = parser.parse_args()

    main(options)