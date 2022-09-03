let WebsocketManager = new WebsocketManagerFactory()
export default WebsocketManager;

function WebsocketManagerFactory() {
    this.connection = null;
    this.state = null;
    this.setState = null;

    this.setStateCallback = function (state, setNewState) {
        this.state = state
        var that = this
        this.setState = function (state) {
            that.state = state;
            setNewState(state);
            console.log("Websocket Manager state", that.state)
        }
    }

    this.start_connection = function () {
        if (!this.connection) {
            this.connection = this.WebsocketConnection()
        }
    }
    this.send_prompt_request = function (prompt) {
        this.connection.send(
            JSON.stringify(
                {
                    "action": "request",
                    "request_type": "prompt",
                    "data": prompt
                }
            )
        )
    }
    this.WebsocketConnection = function () {
        const ws_endpoints = {
            "dev": "wss://dev.ws-api.openimagegenius.com"
        }
        function getTokenCookie() {
            let decodedCookie = decodeURIComponent(document.cookie);
            const cookies = decodedCookie.split(";")
            // console.log(cookies)
            const maybe_tokens = cookies.map(cookie => {
                const cookie_name = cookie.split("=")[0].trim()
                if (cookie_name === "token") {
                    return cookie.split("=")[1].trim()
                }
                return null
            })
            const filtered_maybe_tokens = maybe_tokens.filter(token => token !== null)
            if (filtered_maybe_tokens.length === 1) {
                return filtered_maybe_tokens[0]
            }
            if (filtered_maybe_tokens.length === 0) {
                return null
            }
            console.error("Multiple cookies found, not sure what to do!");
            return -1
        }
        let token = null;
        token = getTokenCookie()
        // console.log("Your token is: ", token)
        if (token === null) {
            // Unauthorized, handle redirect.
        }
        if (token === -1) {
            // Oh no, do something about this
        }

        const websocket = new WebSocket(ws_endpoints["dev"])

        // Register event listeners
        websocket.addEventListener("error", (error) => {
            console.error(error)
        })
        websocket.addEventListener("close", (event) => {
            // console.log("Close event", event)
        })

        websocket.addEventListener("message", (event) => {
            // console.log("Received message ", event)
            const obj = JSON.parse(event.data)
            console.log("Parsed", obj)

            if (obj.message_type === "authorization") {
                if (obj.data === "unauthorized") {
                    this.setState({
                        ...this.state,
                        authorized: false,
                        connected: true
                    })
                }
                if (obj.data === "authorized") {
                    this.setState({
                        ...this.state,
                        authorized: true,
                        connected: true
                    })
                }
            }
            if (obj.message_type === "request_accepted") {
                this.setState({
                    ...this.state,
                    requests: [...this.state.requests, obj]
                })
            }
            if (obj.message_type === "job_complete") {
                let merged_requests = this.state.requests.map(request => {
                    if (request.data.request_id === obj.data.request_id) {
                        return {
                            message_type: obj.data.message_type,
                            data: {
                                ...request.data,
                                ...obj.data
                            }
                        }
                    }
                    return request
                })

                this.setState({
                    ...this.state,
                    requests: merged_requests
                })
            }
        })
        websocket.addEventListener('open', () => {
            websocket.send(
                JSON.stringify(
                    {
                        "action": "authorize",
                        "token": "89480825643960485537603252629543680"
                    }
                )
            )
        })
        return websocket
    }
}
