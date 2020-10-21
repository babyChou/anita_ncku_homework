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
import java.awt.*;
import java.awt.event.*;
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;
import com.mashape.unirest.http.exceptions.UnirestException;
import java.util.regex.*;

public class ChatClient implements Runnable, WindowListener, ActionListener {
    protected String username;
    protected String host;
    protected int port;
    protected Frame frame;
    protected TextArea output;
    protected TextArea side;
    protected TextField input;
    public Frame loginFrame;
    public TextField inputUsername;
    public TextField inputPassword;
    public Label errMsg;

    public ChatClient (String host, int port) {
        this.host = host;
        this.port = port;
        Panel panel = new Panel(new BorderLayout());
        frame = new Frame ("ChatClient [" + host + ':' + port + "]");
        frame.addWindowListener (this);
        output = new TextArea ("", 30, 50, TextArea.SCROLLBARS_VERTICAL_ONLY);
        output.setEditable (false);

        side = new TextArea ("", 30, 20, TextArea.SCROLLBARS_VERTICAL_ONLY);
        side.setEditable (false);


        input = new TextField ();
        input.addActionListener (this);

        panel.add(output, BorderLayout.NORTH);
        panel.add(input, BorderLayout.SOUTH);
        frame.add ("Center", panel);
        frame.add ("West",side);

        frame.pack();
   
    }

    public void Signin() {
        loginFrame = new Frame("ChatClient [" + host + ':' + port + "]");
        loginFrame.addWindowListener(this);
        loginFrame.setLayout(new GridLayout(4, 2));
        Button btn = new Button("OK");
        Button btnAdd = new Button("Add user");
        btn.setActionCommand("ok");
        btn.addActionListener(this);
        btnAdd.setActionCommand("add");
        btnAdd.addActionListener(this);
        inputUsername = new TextField(30);
        inputPassword = new TextField(30);
        errMsg = new Label();

        loginFrame.add(new Label("username:"));
        loginFrame.add(inputUsername);
        loginFrame.add(new Label("password:"));
        loginFrame.add(inputPassword);

        loginFrame.add(errMsg);
        loginFrame.add(new Label(""));

        loginFrame.add(btnAdd);
        loginFrame.add(btn);
        loginFrame.pack();
        loginFrame.setVisible(true);

    }

    protected DataInputStream dataIn;
    protected DataOutputStream dataOut;
    protected Thread listener;

    public synchronized void start () throws IOException {
        if (listener == null) {
            Socket socket = new Socket (host, port);
            try {
                dataIn = new DataInputStream (new BufferedInputStream (socket.getInputStream ()));
                dataOut = new DataOutputStream (new BufferedOutputStream (socket.getOutputStream ()));
                // Pass username
                dataOut.writeUTF (username);
                dataOut.flush ();
            } catch (IOException ex) {
                socket.close ();
                throw ex;
            }
            listener = new Thread (this);
            listener.start ();
            frame.setVisible (true);
            loginFrame.setVisible (false);
        }
    }

    public synchronized void stop () throws IOException {
        frame.setVisible (false);
        if (listener != null) {
          listener.interrupt ();
          listener = null;
          dataOut.close ();
      }
    }

    public void run () {
        try {
            while (!Thread.interrupted ()) {
                String line = dataIn.readUTF ();

                Pattern p = Pattern.compile("[GROUP]");
                Matcher m = p.matcher(line);
                if (m.find()) {
                    side.setText (line);
                }else{
                    output.append (line + "\n");
                }
            }
        }catch (IOException ex) {
          handleIOException (ex);
        }
    }

    protected synchronized void handleIOException (IOException ex) {

        if (listener != null) {
              output.append (ex + "\n");
              input.setVisible (false);
              frame.validate ();
              if (listener != Thread.currentThread ())
                listener.interrupt ();
            listener = null;
            try {
                dataOut.close ();
            } catch (IOException ignored) {}
        }
    }

    public void windowOpened (WindowEvent event) {
        input.requestFocus ();
    }

    public void windowClosing (WindowEvent event) {
        try {
          stop ();
      } catch (IOException ex) {
          ex.printStackTrace ();
      }
    }

    public void windowClosed (WindowEvent event) {}
    public void windowIconified (WindowEvent event) {}
    public void windowDeiconified (WindowEvent event) {}
    public void windowActivated (WindowEvent event) {}
    public void windowDeactivated (WindowEvent event) {}

    public void actionPerformed (ActionEvent event) {
        String cmd = event.getActionCommand();
        try {
            if (cmd == "ok" || cmd == "add") {
                String type = "login";
                try {
                    if(cmd == "add") {
                        type = cmd;
                    }


                    Unirest.setTimeouts(0, 0);
                    HttpResponse<String> response = Unirest.post("http://localhost:8080/QueryServer")
                                                      .header("Content-Type", "application/x-www-form-urlencoded")
                                                      .field("type", type)
                                                      .field("username", inputUsername.getText())
                                                      .field("password", inputPassword.getText())
                                                      .asString();

                    
                    Pattern p = Pattern.compile("ok");
                    Matcher m = p.matcher(response.getBody());
                    if (m.find()) {
                        username = inputUsername.getText();
                        output.append("Hi~ ");
                        start();
                    }else{
                        errMsg.setText(response.getBody());
                    }

                    System.out.println(response.getBody());
                } catch (Exception ex) {
                    System.out.println(ex.getMessage());
                    ex.printStackTrace ();
                }

            }else{            
              input.selectAll ();
              input.setText("");
              dataOut.writeUTF ("[" + username + "]:" + event.getActionCommand ());
              dataOut.flush ();
            }
      } catch (IOException ex) {
          handleIOException (ex);
      }
    }

    public static void main (String[] args) throws IOException {
        if ((args.length != 1) || (args[0].indexOf (':') < 0))
          throw new IllegalArgumentException ("Syntax: ChatClient <host>:<port>");
      int idx = args[0].indexOf (':');
      String host = args[0].substring (0, idx);
      int port = Integer.parseInt (args[0].substring (idx + 1));
      ChatClient client = new ChatClient (host, port);
      client.Signin();
    }
}
