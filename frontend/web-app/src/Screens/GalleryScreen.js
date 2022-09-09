import { useEffect, useState } from "react"

export default function GalleryScreen(props) {
    const [fetched, setFetched] = useState(false)

    useEffect(() => {
        if (fetched === false) {
            props.websockets.manager.send_get_requests()
            setFetched(true)
        }

    }, [fetched, props.websockets.manager])

    return (
        <div>
            Hello Gallery!
        </div>
    )
}