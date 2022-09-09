let WebsocketManager = new WebsocketManagerFactory()
export default WebsocketManager;

function WebsocketManagerFactory() {
    this.connection = null;
    this.state = null;
    this.setState = null;
    this.setNotifications = null;

    this.setStateCallback = function (state, setNewState, setNotifications) {
        this.state = state
        var that = this
        this.setState = function (state) {
            that.state = state;
            that.setNotifications = setNotifications
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
    this.send_get_requests = function () {
        this.connection.send(
            JSON.stringify(
                {
                    "action": "request",
                    "request_type": "get_requests",
                    "data": {
                        "current_page": 0,
                        "page_size": 20,
                    }
                }
            )
        )
    }

    this.WebsocketConnection = function () {
        const ws_endpoints = {
            "dev": "wss://dev.ws-api.openimagegenius.com",
            "prod": "wss://ws-api.openimagegenius.com"
        }
        const stage = process.env.REACT_APP_ENV;
        const ws_endpoint = ws_endpoints[stage];
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

        const websocket = new WebSocket(ws_endpoint)

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

            if (obj.message === "Internal Server Error") {
                this.setNotifications(
                    [{ "message_type": "internal_server_error", "data": "Server Error" }]
                )
                return
            }

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
            if (obj.message_type === "get_requests_response") {
                this.setState({
                    ...this.state,
                    requests: obj.data.requests
                })
                return // No need to notify
            }

            if (obj.message_type === "request_accepted") {
                this.setState({
                    ...this.state,
                    busy: true,
                    requests: [...this.state.requests, obj],
                    recent_requests: [...this.state.recent_requests, obj],

                })
            }

            if (obj.message_type === "job_complete" || obj.message_type === "job_failed") {
                console.log("Got job update", obj.message_type)
                let merged_requests = this.state.requests.map(request => {
                    if (request.data.request_id === obj.data.request_id) {
                        return {
                            message_type: obj.message_type,
                            data: {
                                ...request.data,
                                ...obj.data
                            },
                            busy: false,
                        }
                    }
                    return request
                })
                let merged_recent_requests = this.state.recent_requests.map(request => {
                    if (request.data.request_id === obj.data.request_id) {
                        return {
                            message_type: obj.message_type,
                            data: {
                                ...request.data,
                                ...obj.data
                            },
                            busy: false,
                        }
                    }
                    return request
                })
                this.setState({
                    ...this.state,
                    requests: merged_requests,
                    recent_requests: merged_recent_requests
                })
            }
            this.setNotifications([obj])

        })
        websocket.addEventListener('open', () => {
            websocket.send(
                JSON.stringify(
                    {
                        "action": "authorize",
                        "token": token
                    }
                )
            )
        })
        return websocket
    }
}
