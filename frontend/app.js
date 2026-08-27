const API_URL = "http://127.0.0.1:8000";

let conversation = [];

const chat = document.getElementById("chat");

const questionInput =
    document.getElementById("question");

const sendButton =
    document.getElementById("send");

const newChatButton =
    document.getElementById("newChat");

const departmentSelect =
    document.getElementById("department");

const documentSelect =
    document.getElementById("document");


function addMessage(
    role,
    content,
    sources = []
) {
    const message =
        document.createElement("div");

    message.className =
        `message ${role}`;


    const messageContent =
        document.createElement("div");

    messageContent.className =
        "message-content";

    messageContent.textContent =
        content;

    message.appendChild(
        messageContent
    );


    if (sources.length > 0) {

        const sourcesWrapper =
            document.createElement("div");

        sourcesWrapper.className =
            "sources-wrapper";


        const sourcesHeader =
            document.createElement("button");

        sourcesHeader.className =
            "sources-toggle";

        sourcesHeader.textContent =
            `Sources (${sources.length})`;


        const sourcesList =
            document.createElement("div");

        sourcesList.className =
            "sources-list";

        sourcesList.hidden = true;


        sources.forEach(source => {

            const sourceItem =
                document.createElement("div");

            sourceItem.className =
                "source-item";


            let text =
                source.document ||
                "Unknown document";


            if (source.page) {
                text +=
                    ` — Page ${source.page}`;
            }


            if (
                source.chunk !== null &&
                source.chunk !== undefined
            ) {
                text +=
                    ` — Chunk ${source.chunk}`;
            }


            sourceItem.textContent =
                text;


            sourcesList.appendChild(
                sourceItem
            );
        });


        sourcesHeader.addEventListener(
            "click",
            () => {

                sourcesList.hidden =
                    !sourcesList.hidden;


                sourcesHeader.textContent =
                    sourcesList.hidden
                        ? `Sources (${sources.length})`
                        : `Hide Sources (${sources.length})`;
            }
        );


        sourcesWrapper.appendChild(
            sourcesHeader
        );

        sourcesWrapper.appendChild(
            sourcesList
        );

        message.appendChild(
            sourcesWrapper
        );
    }


    chat.appendChild(message);

    chat.scrollTop =
        chat.scrollHeight;
}


function addLoadingMessage() {

    const message =
        document.createElement("div");

    message.className =
        "message assistant";

    message.id =
        "loading-message";


    const loading =
        document.createElement("div");

    loading.className =
        "loading";

    loading.textContent =
        "Searching the knowledge base...";


    message.appendChild(
        loading
    );

    chat.appendChild(
        message
    );

    chat.scrollTop =
        chat.scrollHeight;
}


function removeLoadingMessage() {

    const loading =
        document.getElementById(
            "loading-message"
        );

    if (loading) {
        loading.remove();
    }
}


function getFilters() {

    const department =
        departmentSelect.value;

    const documentName =
        documentSelect.value;


    const filters = {};


    if (department) {

        filters.department =
            department;
    }


    if (documentName) {

        filters.document_name =
            documentName;
    }


    return filters;
}


async function sendMessage() {

    const question =
        questionInput.value.trim();


    if (!question) {
        return;
    }


    questionInput.value = "";

    sendButton.disabled = true;

    questionInput.disabled = true;


    addMessage(
        "user",
        question
    );


    addLoadingMessage();


    try {

        const filters =
            getFilters();


        const response =
            await fetch(
                `${API_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        question:
                            question,

                        conversation:
                            conversation,

                        filters:
                            filters

                    })
                }
            );


        if (!response.ok) {

            throw new Error(
                `API request failed: ${response.status}`
            );
        }


        const result =
            await response.json();


        conversation =
            result.conversation;


        removeLoadingMessage();


        addMessage(
            "assistant",
            result.answer,
            result.sources
        );


    } catch (error) {

        console.error(error);


        removeLoadingMessage();


        addMessage(
            "assistant",
            "Unable to connect to the RAG API."
        );

    } finally {

        sendButton.disabled =
            false;

        questionInput.disabled =
            false;

        questionInput.focus();
    }
}


sendButton.addEventListener(
    "click",
    sendMessage
);


questionInput.addEventListener(
    "keydown",
    event => {

        if (event.key === "Enter") {

            sendMessage();
        }
    }
);


newChatButton.addEventListener(
    "click",
    () => {
        conversation = [];

        chat.innerHTML = "";

        departmentSelect.value = "";
        documentSelect.value = "";

        questionInput.focus();
    }
);


questionInput.focus();