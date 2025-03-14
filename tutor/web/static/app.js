function DialogueApp() {
    const [dialogue, setDialogue] = React.useState([]);
    const [userInput, setUserInput] = React.useState('');
    const [scenario, setScenario] = React.useState('restaurant');
    const [isStarted, setIsStarted] = React.useState(false);
    const [feedback, setFeedback] = React.useState(null);
    const [suggestedWords, setSuggestedWords] = React.useState([]);

    const startDialogue = async () => {
        const response = await fetch('http://localhost:5001/api/start-dialogue', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ scenario }),
        });
        const data = await response.json();
        setDialogue([{
            role: 'tutor',
            situation_zh: data.situation_zh,
            situation_en: data.situation_en,
            content_zh: data.initial_line_zh,
            content_pinyin: data.initial_line_pinyin,
            content_en: data.initial_line_en,
        }]);
        setIsStarted(true);
        setFeedback(null);
        setSuggestedWords([]);
    };

    const sendResponse = async () => {
        if (!userInput.trim()) return;

        const newDialogue = [...dialogue, {
            role: 'user',
            content_zh: userInput,
        }];

        const response = await fetch('http://localhost:5001/api/respond', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                response: userInput,
                history: dialogue.map(d => ({
                    role: d.role,
                    content: d.content_zh,
                })),
            }),
        });
        const data = await response.json();

        newDialogue.push({
            role: 'tutor',
            content_zh: data.next_line_zh,
            content_pinyin: data.next_line_pinyin,
            content_en: data.next_line_en,
        });

        setDialogue(newDialogue);
        setUserInput('');
        setFeedback(data.evaluation);
        setSuggestedWords(data.suggested_words || []);
    };

    return (
        <div>
            <h1>Chinese Dialogue Practice</h1>
            {!isStarted ? (
                <div className="scenario-selector">
                    <p className="welcome-text">
                        Welcome! Choose a scenario to practice your Chinese conversation skills.
                        Each dialogue will provide translations, pinyin, and helpful vocabulary.
                    </p>
                    <select value={scenario} onChange={(e) => setScenario(e.target.value)}>
                        <option value="restaurant">Restaurant</option>
                        <option value="shopping">Shopping</option>
                        <option value="travel">Travel</option>
                        <option value="work">Work</option>
                    </select>
                    <button onClick={startDialogue}>Start Dialogue</button>
                </div>
            ) : (
                <div className="dialogue-container">
                    {dialogue.map((message, index) => (
                        <div key={index} className={`message ${message.role}-message`}>
                            {message.situation_zh && (
                                <div className="situation-box">
                                    <div className="situation-title">Current Scenario</div>
                                    <div className="chinese-text">{message.situation_zh}</div>
                                    <div className="english">{message.situation_en}</div>
                                </div>
                            )}
                            <div className="chinese-text">{message.content_zh}</div>
                            {message.content_pinyin && (
                                <div className="pinyin">{message.content_pinyin}</div>
                            )}
                            {message.content_en && (
                                <div className="english">{message.content_en}</div>
                            )}
                        </div>
                    ))}

                    {feedback && (
                        <div className="feedback">
                            <h3>Feedback</h3>
                            <p>{feedback}</p>
                        </div>
                    )}

                    {suggestedWords.length > 0 && (
                        <div className="suggested-words">
                            <h3>Useful Words/Phrases</h3>
                            <ul>
                                {suggestedWords.map((word, index) => (
                                    <li key={index}>{word}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <div className="input-area">
                        <textarea
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            placeholder="Type your response in Chinese..."
                            rows="4"
                        />
                        <button onClick={sendResponse}>Send Response</button>
                    </div>
                </div>
            )}
        </div>
    );
}

// Initialize React app
ReactDOM.render(
    <DialogueApp />,
    document.getElementById('root')
);
