/*
 * Java Network Programming, Second Edition
 * Merlin Hughes, Michael Shoffner, Derek Hamner
 * Manning Publications Company; ISBN 188477749X
 *
 * http://nitric.com/jnp/
 *
 * Copyright (c) 1997-1999 Merlin Hughes, Michael Shoffner, Derek Hamner;
 * all rights reserved; see license.txt for details.
 */
package Chat;
import java.io.*;
import java.net.*;
import java.util.*;
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;
import com.mashape.unirest.http.exceptions.UnirestException;

public class ChatServer {
    private int port;

    public ChatServer(int port) {
        this.port = port;
    }

    public void execute() {
        try (ServerSocket serverSocket = new ServerSocket(port)) {
 
            System.out.println("Chat Server is listening on port " + port);
 
            while (true) {
                Socket client = serverSocket.accept();
                System.out.println("New user connected");
                System.out.println ("Accepted from " + client.getInetAddress ());
                ChatHandler handler = new ChatHandler(client, this);
                handler.start();
 
            }
 
        } catch (IOException ex) {
            System.out.println("Error in the server: " + ex.getMessage());
            ex.printStackTrace();
        }
    }

    public static void main (String args[]) throws IOException {
        if (args.length != 1)
            throw new IllegalArgumentException ("Syntax: ChatServer <port>");
        int port = Integer.parseInt (args[0]);
 
        ChatServer server = new ChatServer(port);
        server.execute();
    }

    String getGroup() {
        try {
            Unirest.setTimeouts(0, 0);
            HttpResponse<String> response = Unirest.get("http://localhost:8080/QueryServer").asString();

            return response.getBody();
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
            ex.printStackTrace ();
        }

        return "";
    }

}
