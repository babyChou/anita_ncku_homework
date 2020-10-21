package DBserver;
// Import required java libraries
import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;
import java.sql.*;
import java.util.Properties;
import java.sql.Statement;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.util.HashMap;

// Extend HttpServlet class
public class QueryServer extends HttpServlet {

   private String message;
   private Connection conn = null;
   private Statement stmt = null;
   private ResultSet rs = null;
   // private DBConnection db;

   public static Connection getConnection() throws Exception {
        String driver = "com.mysql.jdbc.Driver";
        Class.forName(driver);

       // Create a connection to the database
        String url = "jdbc:mysql://localhost:3306/java_db?useSSL=false";
        String username = "root";
        String password = "ayumi123";
        return DriverManager.getConnection(url, username, password);
   }

   public void init() throws ServletException {
      // Do required initialization
      message = "Hello World";
   }


   public void doGet(HttpServletRequest request, HttpServletResponse response)
   throws ServletException, IOException {
      String query;

      response.setContentType("text/plain");
      PrintWriter out = response.getWriter();
      try {
         String result = "";
         conn = getConnection();
         stmt = conn.createStatement();
         query = "SELECT * FROM USERINFO";
         rs = stmt.executeQuery(query);
         
      
         while (rs.next()) {
            result += "[" + rs.getString("username") + "]\n";
         }
         out.println(result);

      }catch (Exception e) {
         e.printStackTrace();
         System.err.println(e.getMessage());
      } finally {
         try {
            rs.close();
            stmt.close();
            conn.close();
         } catch (Exception ee) {
            ee.printStackTrace();
         }
      }
      
   }

   // Send request
   // https://stackoverflow.com/questions/3324717/sending-http-post-request-in-java
   public void doPost(HttpServletRequest request, HttpServletResponse response)
   throws ServletException, IOException {

      PrintWriter out = response.getWriter();
      response.setContentType("text/plain");
      response.setCharacterEncoding("UTF-8");
      String type = "";
      String name = "";
      String pwd = "";
      String query = "";
      try {
         type = request.getParameter("type");
         name = request.getParameter("username");
         pwd = request.getParameter("password");

         conn = getConnection();
         stmt = conn.createStatement();
       
         if(type.equals("login")) {
            query = "SELECT * FROM USERINFO U, IDPASSWD I WHERE U.username='" + name + "' AND I.password=md5('"+ pwd +"') AND U.userid=I.userid";
            rs = stmt.executeQuery(query);
            int rowCount = 0;
            while (rs.next()) {
               out.println("ok," + rs.getString("userid") + "," + rs.getString("username"));
               rowCount++;
            }

            if (rowCount == 0) {
               out.println("username or passowrd error");
            }

         }else{
            int result;
            int uid = 0;
            query = "INSERT INTO IDPASSWD (password) VALUES(md5('" + pwd + "'))";
            result = stmt.executeUpdate(query, Statement.RETURN_GENERATED_KEYS);
            rs = stmt.getGeneratedKeys();

            if(rs.next()) {
               uid = rs.getInt(1);
            }
            query = "INSERT INTO USERINFO (userid, username) VALUES(" + uid + ", '" + name + "')";

            result = stmt.executeUpdate(query);
            if ( result == 1 ) {
               out.println("Successful! Please login");
            }
         }
         
      }catch (Exception e) {
         out.println("error! " + e.getMessage());
         e.printStackTrace();
         System.err.println(e.getMessage());
         // System.out.println("Hello World--------------------");
      } finally {
         try {
            rs.close();
            stmt.close();
            conn.close();
         } catch (Exception ee) {
            ee.printStackTrace();
         }
      }

   }

   public void destroy() {
         // do nothing.
   }
}