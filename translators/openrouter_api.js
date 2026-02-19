// Replace with your OpenRouter API key https://openrouter.ai/settings/keys
const API_KEY = 'YOUR_API_KEY_HERE';

//Models and pricing https://openrouter.ai/models
const MODEL = 'meta-llama/llama-3.3-8b-instruct:free';

const API_URL = 'https://openrouter.ai/api/v1/chat/completions';

const PROMPT = 'Translate from SourceLang to TargetLang and return only the translated text';
const MAX_TOKENS = 2000;
const TEMPERATURE = 0.5; // Controls the randomness of the output, lower values are more deterministic and higher values are more random (0 - 2)

const fs = require('fs');
const fetch = require('node-fetch');

async function translate(input) {
    try {
        const { image, sourceLang, targetLang } = JSON.parse(input);
        const prompt = PROMPT.replace('SourceLang', sourceLang).replace('TargetLang', targetLang);
        
        const requestBody = {
            model: MODEL,
            temperature: TEMPERATURE,
            max_tokens: MAX_TOKENS,
            messages: [{
                    role: "user",
                    content: [{
                            type: "text",
                            text: prompt
                        },{
                            type: "image_url",
                            image_url: {
                                url: `data:image/png;base64,${image}`
                            }
                        }
                    ]
                }
            ]
        };

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}`
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`API request failed with status: ${response.status}`);
        }

        const data = await response.json();
        const translatedText = data.choices[0].message.content.trim();
        return translatedText;

    } catch (error) {
        console.error(`Error translating image: ${error}`);
        throw error;
    }
}

module.exports = {
    translate
};
