const { error } = require('console')
const http = require('http')

const PORT = 3000

function check_authorization(authorization=String) {
	
}

const server = http.createServer((req, res) => {
	console.log('Server request')
	res.setHeader("Content-Type", "text/json")

	if (!req.headers['Authorization']) {
		res.writeHead(404)
		res.end(JSON.stringify(
			{status: "error", message: "Invalid authorization"}
		))
		return
	} else {
		res.writeHead(200)

		switch (req.url) {
			case "/left_time":
				res.end(books)
				break
			case "server_status":
				res.end(JSON.stringify(
					{status: "ok", message: "online"}
				))
				break
		}

		res.end()
	}
})

const listener = server.listen(PORT, 'localhost', (error) => {
	if (error) {
		return console.error(error)
	}
	const info = listener.address()
	console.log(`Server is listening on address ${info.address} port ${info.port}`)
})