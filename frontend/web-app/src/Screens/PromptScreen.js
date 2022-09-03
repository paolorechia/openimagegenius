import { useState } from 'react';

import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import { Stack } from '@mui/system';


export default function PromptScreen(props) {

    const [prompt, setPrompt] = useState("")

    function submitPrompt() {
        if (!prompt) {
            console.error("Empty prompt!")
            return;
        }
        console.log("Your prompt is: ", prompt)
        console.log("Submitting...")
        props.websockets.manager.send_prompt_request(prompt)
    }

    function updatePrompt(event) {
        setPrompt(event.target.value)
    }

    return (
        <Stack>
            <TextField
                id="outlined-basic"
                onChange={updatePrompt}
                label="Enter your prompt"
                variant="outlined"
                multiline={true}
                sx={
                    {
                        "maxWidth": "600px",
                    }
                } />
            <Button
                onClick={submitPrompt}
                variant="contained"
                sx={
                    {
                        "marginTop": "60px",
                        "height": "60px",
                        "maxWidth": "200px"
                    }
                }
            >
                Request Generation
            </Button>
        </Stack>
    )
}