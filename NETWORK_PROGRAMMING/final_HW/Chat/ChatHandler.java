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

public class ChatHandler implements Runnable {
  protected Socket socket;
  protected ChatServer server;
  protected String group;
  
  public ChatHandler (Socket socket, ChatServer server) {
    this.socket = socket;
    this.server = server;
    this.group = server.getGroup();
  }

  protected DataInputStream dataIn;
  protected DataOutputStream dataOut;
  protected Thread listener;
  
  public synchronized void start () {
    if (listener == null) {
      try {
        dataIn = new DataInputStream(new BufferedInputStream (socket.getInputStream ()));
        dataOut = new DataOutputStream(new BufferedOutputStream (socket.getOutputStream ()));
        listener = new Thread (this);
        listener.start ();
      } catch (IOException ignored) {
      }
    }
  }

  public synchronized void stop () {
    if (listener != null) {
      try {
        if (listener != Thread.currentThread ())
          listener.interrupt ();
        listener = null;
        dataOut.close ();
      } catch (IOException ignored) {
      }
    }
  }

  protected static Vector handlers = new Vector ();
  
  public void run () {
    try {
      handlers.addElement (this);
      while (!Thread.interrupted ()) {
        String message = dataIn.readUTF();

        broadcast("[GROUP]:\n" + group);
        broadcast(message);
      }
    } catch (EOFException ignored) {
    } catch (IOException ex) {
      if (listener == Thread.currentThread ())
        ex.printStackTrace ();
    } finally {
      handlers.removeElement (this);
    }
    stop ();
  }

  protected void broadcast (String message) {
    synchronized (handlers) {
      Enumeration _enum = handlers.elements ();
      while (_enum.hasMoreElements ()) {
        ChatHandler handler = (ChatHandler) _enum.nextElement ();
        try {
          handler.dataOut.writeUTF (message);
          handler.dataOut.flush ();
        } catch (IOException ex) {
          handler.stop ();
        }
      }
    }
  }
}
