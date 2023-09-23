const { error } = require('console')
const http = require('http')

const PORT = 3000

const server = http.createServer((req, res) => {
	console.log('Server request')

	res.setHeader("Content-Type", "text/json")
	res.writeHead(200)

	const books = JSON.stringify([
		{ title: "The Alchemist", author: "Paulo Coelho", year: 1988 },
		{ title: "The Prophet", author: "Kahlil Gibran", year: 1923 }
	])

	switch (req.url) {
        case "/left_time":
			if (!req.headers['www-authenticate'])

            res.writeHead(200);
            res.end(books);
            break
    }

	res.end()
})

const listener = server.listen(PORT, 'localhost', (error) => {
	if (error) {
		return console.error(error)
	}
	const info = listener.address()
	console.log(`Server is listening on address ${info.address} port ${info.port}`)
})