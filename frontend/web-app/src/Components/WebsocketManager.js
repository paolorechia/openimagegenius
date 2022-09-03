let WebsocketManager = new WebsocketManagerFactory()
export default WebsocketManager;

function WebsocketManagerFactory() {
    this.connection = null;
    this.state = null;
    this.setState = null;

    this.setStateCallback = function (state, setNewState) {
        this.state = state
        this.setState = setNewState
    }

    this.start_connection = function () {
        if (!this.connection) {
            this.connection = WebsocketConnection(this.state, this.setState)
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
}

function WebsocketConnection(state, setState) {
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
                setState({
                    ...state,
                    authorized: false,
                    connected: true
                })
            }
            if (obj.data === "authorized") {
                setState({
                    ...state,
                    authorized: true,
                    connected: true
                })
            }
        }
        if (obj.message_type === "request_accepted") {
            setState({
                ...state,
                requests: [...state.requests, obj]
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