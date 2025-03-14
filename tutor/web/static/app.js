// Add CSS styles
const styles = `
    .spinner {
        display: inline-block;
        width: 12px;
        height: 12px;
        margin-right: 8px;
        border: 2px solid #ffffff;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .display-options,
    .display-toggles {
        margin: 1rem 0;
        display: flex;
        gap: 1rem;
        justify-content: center;
    }

    .display-options label,
    .display-toggles label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
    }

    .input-area {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        padding: 1rem;
        background: #f5f5f5;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .input-controls {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 1rem;
    }

    .input-area textarea {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        resize: vertical;
        font-size: 1rem;
        box-sizing: border-box;
    }

    .display-toggles {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 0.5rem;
    }

    .display-toggles label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #666;
        font-size: 0.9rem;
    }

    .review-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .review-content {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        max-width: 800px;
        max-height: 90vh;
        overflow-y: auto;
        position: relative;
    }

    .review-turn {
        border-bottom: 1px solid #eee;
        padding: 1rem 0;
    }

    .review-turn:last-child {
        border-bottom: none;
    }

    .close-review {
        position: sticky;
        bottom: 0;
        width: 100%;
        padding: 1rem;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        margin-top: 1rem;
    }

    .close-review:hover {
        background: #0056b3;
    }

    .review-button, .send-button {
        background: #007bff;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        min-width: 120px;
        justify-content: center;
    }

    .review-button:hover, .send-button:hover {
        background: #0056b3;
    }

    .review-button:disabled, .send-button:disabled {
        background: #ccc;
        cursor: not-allowed;
    }

    .review-section {
        margin: 1.5rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
    }

    .review-section h3 {
        color: #2c3e50;
        margin-bottom: 1rem;
    }

    .review-section ul {
        margin: 0;
        padding-left: 1.5rem;
    }

    .review-section li {
        margin: 0.5rem 0;
        line-height: 1.5;
    }

    .vocab-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }

    .vocab-item {
        background: white;
        padding: 1rem;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .vocab-item .word {
        font-size: 1.2em;
        font-weight: bold;
        color: #2c3e50;
    }

    .vocab-item .pinyin {
        color: #666;
        font-style: italic;
    }

    .vocab-item .meaning {
        margin: 0.5rem 0;
        color: #2c3e50;
    }

    .vocab-item .usage-note {
        font-size: 0.9em;
        color: #666;
        border-top: 1px solid #eee;
        padding-top: 0.5rem;
        margin-top: 0.5rem;
    }

    .grammar-feedback-list {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .grammar-feedback-item {
        background: white;
        padding: 1rem;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .grammar-comparison {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .grammar-comparison .original {
        color: #e74c3c;
    }

    .grammar-comparison .correction {
        color: #27ae60;
    }

    .explanation, .example {
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid #eee;
    }
`;

// Add the style to the document
const styleSheet = document.createElement("style");
styleSheet.innerText = styles;
document.head.appendChild(styleSheet);

function DialogueApp() {
    const [dialogue, setDialogue] = React.useState([]);
    const [userInput, setUserInput] = React.useState('');
    const [scenario, setScenario] = React.useState('restaurant');
    const [isStarted, setIsStarted] = React.useState(false);
    const [isLoading, setIsLoading] = React.useState(false);
    const [showPinyin, setShowPinyin] = React.useState(false);
    const [showEnglish, setShowEnglish] = React.useState(false);
    const [isReviewing, setIsReviewing] = React.useState(false);
    const [review, setReview] = React.useState(null);

    const startDialogue = async () => {
        if (isLoading) return;
        setIsLoading(true);
        try {
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
                situation_en: showEnglish ? data.situation_en : null,
                content_zh: data.initial_line_zh,
                content_pinyin: showPinyin ? data.initial_line_pinyin : null,
                content_en: showEnglish ? data.initial_line_en : null,
            }]);
            setIsStarted(true);
            setReview(null);
        } catch (error) {
            console.error('Error starting dialogue:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const sendResponse = async () => {
        if (!userInput.trim() || isLoading) return;

        setIsLoading(true);
        try {
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
                    scenario: scenario,
                    include_translations: showPinyin || showEnglish,
                }),
            });
            const data = await response.json();

            // Continue with dialogue

            newDialogue.push({
                role: 'tutor',
                content_zh: data.next_line_zh,
                content_pinyin: showPinyin ? data.next_line_pinyin : null,
                content_en: showEnglish ? data.next_line_en : null,
            });

            setDialogue(newDialogue);
            setUserInput('');
        } catch (error) {
            console.error('Error sending response:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <h1>Chinese Dialogue Practice</h1>
            {!isStarted ? (
                <div className="scenario-selector">
                    <p className="welcome-text">
                        Welcome! Choose a scenario to practice your Chinese conversation skills.
                        You can toggle translations and pinyin as needed.
                    </p>
                    <div className="display-options">
                        <label>
                            <input
                                type="checkbox"
                                checked={showPinyin}
                                onChange={(e) => setShowPinyin(e.target.checked)}
                            />
                            Show Pinyin
                        </label>
                        <label>
                            <input
                                type="checkbox"
                                checked={showEnglish}
                                onChange={(e) => setShowEnglish(e.target.checked)}
                            />
                            Show English
                        </label>
                    </div>
                    <select
                        value={scenario}
                        onChange={(e) => setScenario(e.target.value)}
                        disabled={isLoading}
                    >
                        <option value="restaurant">Restaurant</option>
                        <option value="shopping">Shopping</option>
                        <option value="travel">Travel</option>
                        <option value="work">Work</option>
                    </select>
                    <button
                        onClick={startDialogue}
                        disabled={isLoading}
                    >
                        {isLoading ? 'Starting...' : 'Start Dialogue'}
                    </button>
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
                            {showPinyin && message.content_pinyin && (
                                <div className="pinyin">{message.content_pinyin}</div>
                            )}
                            {showEnglish && message.content_en && (
                                <div className="english">{message.content_en}</div>
                            )}
                        </div>
                    ))}



                    {isReviewing && review && (
                        <div className="review-overlay">
                            <div className="review-content">
                                <h2>Conversation Review</h2>

                                <div className="review-section">
                                    <h3>Overall Feedback</h3>
                                    <p>{review.overall_feedback}</p>
                                </div>





                                <div className="review-section">
                                    <h3>Grammar Feedback</h3>
                                    <div className="grammar-feedback-list">
                                        {review.grammar_feedback.map((feedback, i) => (
                                            <div key={i} className="grammar-feedback-item">
                                                <div className="grammar-comparison">
                                                    <div className="original">
                                                        <strong>Original:</strong> {feedback.original}
                                                    </div>
                                                    <div className="correction">
                                                        <strong>More Natural:</strong> {feedback.correction}
                                                    </div>
                                                </div>
                                                <div className="explanation">
                                                    <strong>Why:</strong> {feedback.explanation}
                                                </div>
                                                <div className="example">
                                                    <strong>Example:</strong> {feedback.example}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="review-section">
                                    <h3>Vocabulary Review</h3>
                                    <div className="vocab-grid">
                                        {review.vocabulary_review.map((item, i) => (
                                            <div key={i} className="vocab-item">
                                                <div className="word">{item.word}</div>
                                                <div className="pinyin">{item.pinyin}</div>
                                                <div className="meaning">{item.meaning}</div>
                                                <div className="usage-note">{item.usage_note}</div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <button
                                    onClick={() => {
                                        setIsReviewing(false);
                                        setReview(null);
                                    }}
                                    className="close-review"
                                >
                                    Close Review
                                </button>
                            </div>
                        </div>
                    )}

                    <div className="input-area">
                        <div className="display-toggles">
                            <label>
                                <input
                                    type="checkbox"
                                    checked={showPinyin}
                                    onChange={(e) => setShowPinyin(e.target.checked)}
                                />
                                Show Pinyin
                            </label>
                            <label>
                                <input
                                    type="checkbox"
                                    checked={showEnglish}
                                    onChange={(e) => setShowEnglish(e.target.checked)}
                                />
                                Show English
                            </label>
                        </div>
                        <textarea
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    sendResponse();
                                }
                            }}
                            placeholder="Type your response in Chinese..."
                            rows="4"
                            disabled={isLoading}
                        />
                        <div className="input-controls">
                            <button
                                onClick={sendResponse}
                                disabled={isLoading}
                                className="send-button"
                            >
                                {isLoading ? (
                                    <>
                                        <span className="spinner"></span>
                                        Sending...
                                    </>
                                ) : 'Send Response'}
                            </button>
                            <button
                                onClick={async () => {
                                    setIsLoading(true);
                                    try {
                                        const response = await fetch('http://localhost:5001/api/review', {
                                            method: 'POST',
                                            headers: {
                                                'Content-Type': 'application/json',
                                            },
                                            body: JSON.stringify({
                                                history: dialogue.map(d => ({
                                                    role: d.role,
                                                    content: d.content_zh,
                                                })),
                                                scenario: scenario,
                                            }),
                                        });
                                        const data = await response.json();
                                        setReview(data);
                                        setIsReviewing(true);
                                    } catch (error) {
                                        console.error('Error getting review:', error);
                                    } finally {
                                        setIsLoading(false);
                                    }
                                }}
                                disabled={isLoading || dialogue.length < 2}
                                className="review-button"
                            >
                                Review My Chinese
                            </button>
                        </div>
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
