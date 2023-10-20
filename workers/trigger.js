addEventListener('scheduled', event => {
    event.waitUntil(
        handleSchedule(event.scheduledTime)
    )
})

async function handleSchedule(scheduledDate) {
    let deployHook = DEPLOY_HOOK;
    const response = await fetch(deployHook, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
    });
    return response;
};