let WebsocketManager = new WebsocketManagerFactory()
export default WebsocketManager;

function mergeRequests(stateRequests, incomingRequests) {
    let by_request_ids = {}
    for (let i = 0; i < stateRequests.length; i++) {
        by_request_ids[stateRequests[i].request_id] = stateRequests[i]
    }
    for (let j = 0; j < incomingRequests.length; j++) {
        let request = incomingRequests[j]
        if (!by_request_ids[request.request_id]) {
            by_request_ids[request.request_id] = request
        } else {
            by_request_ids[request.request_id] = {
                ...by_request_ids[request.request_id],
                ...request
            }
        }
    }
    let merged_requests = []
    Object.keys(by_request_ids).forEach(key => {
        merged_requests.push(by_request_ids[key])
    })
    return merged_requests
}

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
        const last_evaluated_key = this.state.last_evaluated_key
        this.connection.send(
            JSON.stringify(
                {
                    "action": "request",
                    "request_type": "get_requests",
                    "data": {
                        "last_evaluated_key": last_evaluated_key,
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
                const newStateRequests = mergeRequests(this.state.requests, obj.data.requests)
                this.setState({
                    ...this.state,
                    requests: newStateRequests,
                    last_evaluated_key: obj.pagination.last_evaluated_key
                })
                return // No need to notify
            }

            if (obj.message_type === "request_accepted" || obj.message_type === "lambda_scheduled") {
                this.setState({
                    ...this.state,
                    busy: true,
                    requests: [...this.state.requests, obj],
                    recent_requests: [obj, ...this.state.recent_requests],

                })
            }

            if (obj.message_type === "job_complete" || obj.message_type === "job_failed") {
                console.log("Got job update", obj.message_type)
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
                let newState = {
                    recent_requests: merged_recent_requests,
                    busy: false
                }

                if (obj.message_type === "job_complete") {
                    newState.current_image = obj.data
                }

                this.setState({
                    ...this.state,
                    ...newState
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
