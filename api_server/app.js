const { error } = require('console')
const http = require('http')

const PORT = 3000

const server = http.createServer((req, res) => {
	console.log('Server request')

	res.setHeader("content-type")

	res.write('Hello world!')
	res.end()
})

// const listener = server.listen(PORT, 'localhost', (error) => {
// 	if (error) {
// 		return console.error(error)
// 	}
// 	const info = listener.address()
// 	console.log(`Server is listening on address ${info.address} port ${info.port}`)
// })