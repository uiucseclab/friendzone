# friendzone

Author: James Beck

###About

This script is a type of intrusion detection system.

It's intended for servers that really only run one service on one port, for example a web server that's running an online game. The idea for this script came about because I wanted a way for players to be able to connect to a server I host during ddos attacks.

Essentially this script works as a proxy: players connect to it instead of the actual game service. The program also keeps track of the time an ip is connected to the server, and stores that in a database. This is the key to the program. If the server comes under attack, the server owner can set the script to protection mode. In this mode, the script will only allow IPs that are above a certain threshold of connection time to connect to the game server. This way, people who are regular players can still connect and play, and won't have to compete with the attack traffic.

Obviously this script is not meant to be used for services that get a lot of "visitor" traffic, such as for a website. It also requires that the server's firewall be properly configured, otherwise people can just bypass the proxy and connect to the service it's protecting directly.

###Usage
The first time the script runs, it will create a database file called *friendzone.db*. This is where all the IPs and their connection times are stored.

In order to work properly, you must have the script listening on whatever port the service you wish to protect normally uses. This means that you'll have to run that service on a different port.

Once you've done that, you can launch the script by running *python guardian.py <port to listen on> <port to forward connections to>*. It's recommended to run the script as a deamon via *screen*

There are a couple options you can tweak in *guardian.py*:
- *threshold*
  - This is how long a player must be connected before they are considered a "friend". Default is 5 days (in seconds)
- *forward_ip*
  - By default this is *localhost*. I wouldn't recommend running it on a different machine, as that will really only increase delay between connections without providing any great benefits
- *conn*
  - If for whatever reason you don't want to use the default *friendzone.db* database file, you can change that here
- *delay* and *buffer_size*
  - I wouldn't recommend changing these, but you can if you want to.
  
While running, there are several commands you can execute from within the script
- **protect**
  - This will put the script in protection mode and start filtering IP addresses
- **relax**
  - This disables protection and allows any IP to connect again
- **stop**
  - Stops the service
  
If, for whatever reason, you want to erase all IPs that are stored, simply erase the *friendzone.db* file.
