import { useEffect, useState } from "react"
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Button from '@mui/material/Button';

let default_size = 256


export default function GalleryScreen(props) {
    const [fetched, setFetched] = useState(false)
    let len = 0
    let maxWidth = 300
    let minWidth = 300
    let width = 300
    let numberCols = 1

    function loadMore() {
        props.websockets.manager.send_get_requests()
    }

    useEffect(() => {
        if (fetched === false) {
            props.websockets.manager.send_get_requests()
            setFetched(true)
        }
    }, [fetched, props.websockets.manager, len])

    len = props.websockets.state.requests.length
    if (window.screen) {
        maxWidth = window.screen.width - 600;
        width = Math.max(maxWidth, minWidth)
        numberCols = Math.floor(width / default_size)
    }
    console.log(default_size, width, numberCols)

    return (
        <div>
            <ImageList sx={{
                width: width,
                height: "100%",
                overflow: "hidden"
            }}
                cols={numberCols}
                rowHeight={default_size}>
                {props.websockets.state.requests.map((item) => (
                    <ImageListItem key={item.request_id}>
                        <img
                            src={`${item.s3_url}`}
                            srcSet={`${item.s3_url}`}
                            alt={item.data}
                            loading="lazy"
                        />
                    </ImageListItem>
                ))}
            </ImageList>
            {props.websockets.state.last_evaluated_key
                ? <Button onClick={loadMore}> Load more!</Button>
                : "End of list"
            }

        </div>

    )
}