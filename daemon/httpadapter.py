# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
daemon.httpadapter
~~~~~~~~~~~~~~~~~

This module provides a http adapter object to manage and persist 
http settings (headers, bodies). The adapter supports both
raw URL paths and RESTful route definitions, and integrates with
Request and Response objects to handle client-server communication.
"""

from .request import Request
from .response import Response
from .dictionary import CaseInsensitiveDict

class HttpAdapter:
    """
    A mutable :class:`HTTP adapter <HTTP adapter>` for managing client connections
    and routing requests.

    The `HttpAdapter` class encapsulates the logic for receiving HTTP requests,
    dispatching them to appropriate route handlers, and constructing responses.
    It supports RESTful routing via hooks and integrates with :class:`Request <Request>` 
    and :class:`Response <Response>` objects for full request lifecycle management.

    Attributes:
        ip (str): IP address of the client.
        port (int): Port number of the client.
        conn (socket): Active socket connection.
        connaddr (tuple): Address of the connected client.
        routes (dict): Mapping of route paths to handler functions.
        request (Request): Request object for parsing incoming data.
        response (Response): Response object for building and sending replies.
    """

    __attrs__ = [
        "ip",
        "port",
        "conn",
        "connaddr",
        "routes",
        "request",
        "response",
    ]

    def __init__(self, ip, port, conn, connaddr, routes):
        """
        Initialize a new HttpAdapter instance.

        :param ip (str): IP address of the client.
        :param port (int): Port number of the client.
        :param conn (socket): Active socket connection.
        :param connaddr (tuple): Address of the connected client.
        :param routes (dict): Mapping of route paths to handler functions.
        """

        #: IP address.
        self.ip = ip
        #: Port.
        self.port = port
        #: Connection
        self.conn = conn
        #: Conndection address
        self.connaddr = connaddr
        #: Routes
        self.routes = routes
        #: Request
        self.request = Request()
        #: Response
        self.response = Response()

    def handle_client(self, conn, addr, routes):
        """
        Handle an incoming client connection.

        This method reads the request from the socket, prepares the request object,
        invokes the appropriate route handler if available, builds the response,
        and sends it back to the client.

        :param conn (socket): The client socket connection.
        :param addr (tuple): The client's address.
        :param routes (dict): The route mapping for dispatching requests.
        """

        # Connection handler.
        self.conn = conn        
        # Connection address.
        self.connaddr = addr
        # Request handler
        req = self.request
        # Response handler
        resp = self.response

        # Handle the request - đọc cho đến khi có \r\n\r\n (kết thúc headers)
        # msg = conn.recv(1024).decode()
        # req.prepare(msg, routes)
        msg = ""
        raw_data = ""
        while "\r\n\r\n" not in raw_data:
            chunk = conn.recv(1024)
            if not chunk:
                break
            raw_data += chunk
        
        # Tách headers và body
        if "\r\n\r\n" in raw_data:
            header_end = raw_data.find("\r\n\r\n")
            headers_part = raw_data[:header_end + 4]  # Bao gồm \r\n\r\n
            body_part = raw_data[header_end + 4:]
            
            # Prepare request với headers
            req.prepare(headers_part, routes)
            
            # Gán body vào request
            req.body = body_part
        else:
            req.prepare(raw_data, routes)
            req.body = ""
        
        msg = raw_data  # Để compatibility

        # Handle request hook
        if req.hook:
            print("[HttpAdapter] hook in route-path METHOD {} PATH {}".format(req.hook._route_path,req.hook._route_methods))
            req.hook(headers = "bksysnet",body = "get in touch")
            #
            # TODO: handle for App hook here
            #

        # ========== TASK 1: HTTP Server with Cookie Session ==========
        # response = resp.build_response(req)
        # Task 1A: Xử lý POST /login
        if req.method == 'POST' and req.path == '/login':
            print "[HttpAdapter] Task 1A: Processing POST /login"
            
            # Xử lý credentials từ request body
            username = None
            password = None
            
            # Parse body (form-urlencoded: username=admin&password=password)
            if hasattr(req, 'body') and req.body:
                try:
                    params = {}
                    for pair in req.body.split('&'):
                        if '=' in pair:
                            key, val = pair.split('=', 1)
                            params[key] = val
                    username = params.get('username', '')
                    password = params.get('password', '')
                except:
                    pass
            
            # Validate credentials
            if username == 'admin' and password == 'password':
                # Login hợp lệ - gửi trang index với Set-Cookie
                print "[HttpAdapter] Login successful for user: {}".format(username)
                
                # Set response status
                resp.status_code = 200
                resp.reason = 'OK'
                
                # Thêm Set-Cookie header
                resp.headers['Set-Cookie'] = 'auth=true'
                
                # Load nội dung index.html
                base_dir = 'www'
                c_len, resp._content = resp.build_content('/index.html', base_dir)
                resp.headers['Content-Type'] = 'text/html'
                resp.headers['Content-Length'] = str(c_len)
                
                # Build response thủ công
                response_line = "HTTP/1.1 {} {}\r\n".format(resp.status_code, resp.reason)
                header_lines = ""
                for key, val in resp.headers.items():
                    header_lines += "{}: {}\r\n".format(key, val)
                response = response_line + header_lines + "\r\n"
                response = response.encode('utf-8') + resp._content
            else:
                # Login không hợp lệ - trả 401
                print "[HttpAdapter] Login failed - invalid credentials"
                resp.status_code = 401
                resp.reason = 'Unauthorized'
                response = resp.build_notfound()  # Hoặc tự build 401
                # Có thể tự build 401:
                # response = (
                #     "HTTP/1.1 401 Unauthorized\r\n"
                #     "Content-Type: text/plain\r\n"
                #     "Content-Length: 13\r\n"
                #     "Connection: close\r\n"
                #     "\r\n"
                #     "401 Unauthorized"
                # ).encode('utf-8')
        
        # Task 1B: Kiểm soát truy cập bằng Cookie cho GET
        elif req.method == 'GET':
            print "[HttpAdapter] Task 1B: Processing GET {}".format(req.path)
            
            # Extract cookie từ request headers
            cookie_header = req.headers.get('cookie', '')
            auth_cookie = None
            
            if cookie_header:
                # Parse cookie: "auth=true; other=value"
                for pair in cookie_header.split(';'):
                    pair = pair.strip()
                    if '=' in pair:
                        key, val = pair.split('=', 1)
                        if key == 'auth':
                            auth_cookie = val
            
            print "[HttpAdapter] Cookie auth={}".format(auth_cookie)
            
            # Kiểm tra cookie
            if auth_cookie == 'true':
                # Cookie hợp lệ - serve nội dung bình thường
                print "[HttpAdapter] Cookie valid - serving content"
                response = resp.build_response(req)
            else:
                # Cookie không hợp lệ - trả 401
                print "[HttpAdapter] Cookie invalid or missing - return 401"
                resp.status_code = 401
                resp.reason = 'Unauthorized'
                response = (
                    "HTTP/1.1 401 Unauthorized\r\n"
                    "Content-Type: text/plain\r\n"
                    "Content-Length: 28\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                    "401 Unauthorized - No Cookie"
                ).encode('utf-8')
        else:
            # Các method khác (PUT, DELETE, etc.) - xử lý bình thường
            response = resp.build_response(req)

        #print(response)
        conn.sendall(response)
        conn.close()

    @property
    def extract_cookies(self, req, resp):
        """
        Build cookies from the :class:`Request <Request>` headers.

        :param req:(Request) The :class:`Request <Request>` object.
        :param resp: (Response) The res:class:`Response <Response>` object.
        :rtype: cookies - A dictionary of cookie key-value pairs.
        """
        cookies = {}
        for header in headers:
            if header.startswith("Cookie:"):
                cookie_str = header.split(":", 1)[1].strip()
                for pair in cookie_str.split(";"):
                    key, value = pair.strip().split("=")
                    cookies[key] = value
        return cookies

    def build_response(self, req, resp):
        """Builds a :class:`Response <Response>` object 

        :param req: The :class:`Request <Request>` used to generate the response.
        :param resp: The  response object.
        :rtype: Response
        """
        response = Response()

        # Set encoding.
        response.encoding = get_encoding_from_headers(response.headers)
        response.raw = resp
        response.reason = response.raw.reason

        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = req.url

        # Add new cookies from the server.
        response.cookies = extract_cookies(req)

        # Give the Response some context.
        response.request = req
        response.connection = self

        return response

    # def get_connection(self, url, proxies=None):
        # """Returns a url connection for the given URL. 

        # :param url: The URL to connect to.
        # :param proxies: (optional) A Requests-style dictionary of proxies used on this request.
        # :rtype: int
        # """

        # proxy = select_proxy(url, proxies)

        # if proxy:
            # proxy = prepend_scheme_if_needed(proxy, "http")
            # proxy_url = parse_url(proxy)
            # if not proxy_url.host:
                # raise InvalidProxyURL(
                    # "Please check proxy URL. It is malformed "
                    # "and could be missing the host."
                # )
            # proxy_manager = self.proxy_manager_for(proxy)
            # conn = proxy_manager.connection_from_url(url)
        # else:
            # # Only scheme should be lower case
            # parsed = urlparse(url)
            # url = parsed.geturl()
            # conn = self.poolmanager.connection_from_url(url)

        # return conn


    def add_headers(self, request):
        """
        Add headers to the request.

        This method is intended to be overridden by subclasses to inject
        custom headers. It does nothing by default.

        
        :param request: :class:`Request <Request>` to add headers to.
        """
        pass

    def build_proxy_headers(self, proxy):
        """Returns a dictionary of the headers to add to any request sent
        through a proxy. 

        :class:`HttpAdapter <HttpAdapter>`.

        :param proxy: The url of the proxy being used for this request.
        :rtype: dict
        """
        headers = {}
        #
        # TODO: build your authentication here
        #       username, password =...
        # we provide dummy auth here
        #
        username, password = ("user1", "password")

        if username:
            headers["Proxy-Authorization"] = (username, password)

        return headers