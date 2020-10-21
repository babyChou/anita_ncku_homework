# export CLASSPATH=$CLASSPATH:./jar_files/*
javac DBserver/*.java -d /usr/local/apache-tomcat/webapps/ROOT/WEB-INF/classes
javac Chat/*.java
# java Chat.ChatServer 3333
# java Chat.ChatClient 127.0.0.1:3333
# sudo sh /usr/local/apache-tomcat/bin/catalina.sh run;
# sh /usr/local/apache-tomcat/bin/startup.sh run 
# sh /usr/local/apache-tomcat/bin/shutdown.sh
