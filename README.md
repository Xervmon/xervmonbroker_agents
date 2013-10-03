xervmonbroker_agents
====================

Downloable agents for Customers.

Using the RPM / DEB packages
Installing the Agent via RPM or DEB is very easy. All you have to do is to make sure xinetd is installed first and then install the package. Usually, you'll also want to install the logwatch extension. 

Run as SUDO or root password/
For RPM this is done using: 

root@linux# rpm -i xervmon_broker-agent-1.2.3i2-1.noarch.rpm

root@linux# rpm -i xervmon_broker-agent-logwatch-1.2.3i2-1.noarch.rpm 

For DEB type distros: 

root@linux# dpkg -i xervmon-broker-agent_1.2.3i2-2_all.deb

root@linux# dpkg -i xervmon-broker-agent-logwatch_1.2.3i2-2_all.deb 


Installing the agent Manually

The xervmon_broker agent for Linux consists of only two files: a shell skript called xervmon_broker_agent.linux and a configuration file for xinetd.conf, both of which can be found in the subdirectory agents. xinetd is an improved version of the classical inetd and a is available or even standard on most current linux distributions. 
Alternatively you can use the classical inetd, but this documentation focusses on xinetd. 
Please install the file xervmon_broker_agent.linux on your target host as /usr/bin/xervmon_broker_agent (drop the .linux). You should be able to execute the agent simply by calling it from the command line. It can be run as non-root user, but some diagnostic information can only be retrieved if it is run as root. The output of xervmon_broker_agent looks like this (abbreviated): 


The agent is a binary Hence you need to run the xinetd to have it run all the time.
