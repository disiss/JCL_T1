const http = require('http')
const net = require('net')
const url = require('url')
const fs = require("fs")

function get_hostname() {
	http.get("http://ipinfo.io/ip", (resp) => {
		let data = '';

		// чанк который был получен, добавляем в data
		resp.on('data', (chunk) => {
			data += chunk;
		});

		// как только получили всю информацию
		resp.on('end', () => {
			return data
		});

	}).on("error", (err) => {
		console.log("Error: " + err.message);
	});
}

const hostname = get_hostname()
const port = 1991

function check_auth(login = String, password = String) {
	const fileList = fs.readdirSync("users")

	// console.log(fileList)

	let status = false

	for (const file of fileList) {
		const result = fs.readFileSync(`users/${file}`, { encoding: "utf-8" })

		const auth_conf = JSON.parse(result)
			
		if (auth_conf.login === login && auth_conf.password === password) {
			console.log("auth ok!")
			status = true
			break
		} else {
			console.log("auth not ok!")
			return;
		}
	}
	return status
}

const requestHandler = (req, res) => { // discard all request to proxy server except HTTP/1.1 CONNECT method
	res.writeHead(405, {'Content-Type': 'text/plain'})
	res.end('Method not allowed')
}

const server = http.createServer(requestHandler)

const listener = server.listen(port, hostname, (err) => {
	if (err) {
		return console.error(err)
	}
	const info = listener.address()
	console.log(`Server is listening on address ${info.address} port ${info.port}`)
})

server.on('connect', (req, clientSocket, head) => { // listen only for HTTP/1.1 CONNECT method
	// console.log(clientSocket.remoteAddress, clientSocket.remotePort, req.method, req.url)

	if (!req.headers['proxy-authorization']) { // here you can add check for any username/password, I just check that this header must exist!
		clientSocket.write([
			'HTTP/1.1 407 Proxy Authentication Required',
			'Proxy-Authenticate: Basic realm="proxy"',
			'Proxy-Connection: close',
		].join('\r\n'))
		clientSocket.end('\r\n\r\n')    // empty body
		return
	} else {
		auth_info = Buffer.from(req.headers['proxy-authorization'].split(' ')[1], 'base64').toString('utf-8').split(':')
		login = auth_info[0]
		password = auth_info[1]

		console.log("test", check_auth(login=login, password=password))

		if (check_auth(login=login, password=password) === false) {
			clientSocket.write([
				'HTTP/1.1 407 Proxy Authentication Required',
				'Proxy-Authenticate: Basic realm="proxy"',
				'Proxy-Connection: close',
			].join('\r\n'))
			clientSocket.end('\r\n\r\n')    // empty body
			return
		}
	}

	const {port, hostname} = url.parse(`//${req.url}`, false, true) // extract destination host and port from CONNECT request
	if (hostname && port) {
		console.log("GO")

		const serverErrorHandler = (err) => {
			console.error(err.message)
			if (clientSocket) {
				clientSocket.end(`HTTP/1.1 500 ${err.message}\r\n`)
			}
		}

		const serverEndHandler = () => {
			if (clientSocket) {
				clientSocket.end(`HTTP/1.1 500 External Server End\r\n`)
			}
		}

		const serverSocket = net.connect(port, hostname) // connect to destination host and port
		const clientErrorHandler = (err) => {
			console.error(err.message)
			if (serverSocket) {
				serverSocket.end()
			}
		}

		const clientEndHandler = () => {
			if (serverSocket) {
				serverSocket.end()
			}
		}

		clientSocket.on('error', clientErrorHandler)
		clientSocket.on('end', clientEndHandler)
		serverSocket.on('error', serverErrorHandler)
		serverSocket.on('end', serverEndHandler)
		serverSocket.on('connect', () => {
			clientSocket.write([
				'HTTP/1.1 200 Connection Established',
				'Proxy-agent: Junction-HTTP-PROXY',
			].join('\r\n'))
			serverSocket.write(head)

			clientSocket.write('\r\n\r\n') // empty body
			// "blindly" (for performance) pipe client socket and destination socket between each other
			serverSocket.pipe(clientSocket, {end: false})
			clientSocket.pipe(serverSocket, {end: false})
		})
		} else {
			clientSocket.end('HTTP/1.1 400 Bad Request\r\n')
			clientSocket.destroy()
		}
})