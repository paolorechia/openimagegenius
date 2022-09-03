import { useState } from 'react';

import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import { Stack } from '@mui/system';
import Box from '@mui/material/Box';


export default function PromptScreen(props) {

    const [prompt, setPrompt] = useState("")
    const jobs_completed = props.websockets.state.requests.filter(req => req.message_type === "job_complete")
    let last_completed_job = null;
    if (jobs_completed.length > 0) {
        last_completed_job = jobs_completed[jobs_completed.length - 1]
        console.log(last_completed_job)
    }

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
            <Box sx={{ padding: "50px" }}>
                {last_completed_job !== null
                    ? <img src={last_completed_job.data.s3_url} width="500px" height="500px" alt={last_completed_job.data.prompt} />
                    : "Go ahead"
                }
            </Box>
        </Stack>
    )
}