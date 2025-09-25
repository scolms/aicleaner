🌍 We’re living through an AI revolution

History has always been shaped by moments of transformation — the printing press, the industrial revolution, the internet. Today, we’re experiencing the next seismic shift: the rise of artificial intelligence.

This isn’t just about faster search or smarter chatbots. It’s about reimagining how we work, create, and solve problems.

Businesses can automate what once felt impossible.

Small teams can compete with giants.

Individuals can amplify creativity, insight, and impact like never before.

The real story of the AI revolution isn’t about replacing people. It’s about empowering them — giving us tools to think bigger, move faster, and unlock ideas that were once out of reach.

🚀 The companies, communities, and individuals who embrace this shift won’t just keep pace — they’ll set the pace.

The question isn’t if AI will change your industry. The question is: how are you preparing to be part of that change?

#AI #Innovation #FutureOfWork #AIRevolutionSpeed v Accuracy

Scott Colebourn 

Founder / CEO / CTO | AI Platform Architect | Ex-Microsoft & Allianz
September 19, 2025
The Heuristic Application Logic Paradox
// A Friday post that is not about the industrial revolution //
Historically, the data-to-knowledge transformation at the heart of IT systems has been deterministic. Interpretation of data and extraction of information has always been rule-based:
•	How many customers do we have? Read the customer table, filter for active records, count → easy.
•	Which product sells the most? Read sales, group by product, sort on totals → fairly easy.
•	Which customers only bought in March? Query customers, join to sales, apply date filter, summarise → easy-ish.
But:
•	Which overseas Healthcare customers bought product A then product B, but not Product C, and how do their purchase habits differ from UK Healthcare customers? Suddenly we’re in complex query territory. It’s still possible, but the effort needed (joins, rules, edge cases) grows rapidly, along with the risk of error and cost of maintenance.
________________________________________
Enter heuristic logic (LLMs)
Instead of painstakingly encoding every rule, we can hand the intent and the data to a large language model and ask it to derive an answer.
•	This is logic-free in the traditional sense: no hard-coded business rules, just heuristic pattern matching and reasoning.
•	LLMs are excellent at both data processing (pattern recognition) and natural language expression, so for the majority of cases they return the right transformation, faster and more flexibly than writing bespoke rules.
________________________________________
The paradox
•	Deterministic logic guarantees correctness but scales poorly with complexity.
•	Heuristic logic scales beautifully with complexity but cannot guarantee correctness.
This is the Heuristic Application Logic Paradox: the more complex the transformation, the more appealing heuristics become — even though they are less certain.
________________________________________
Why “mostly right” is sometimes enough
In business, there are times when having information that is mostly right is far more valuable than having no information at all.
•	A marketing team that can identify most of the likely overseas Healthcare customers is better off than one waiting months for a perfect query to be engineered.
•	A manager seeing an 80% accurate trend report can take faster, more competitive action than one left in the dark.
LLM-based heuristic processes provide this capability. They unlock insights that would otherwise be too complex or costly to encode deterministically, delivering value now rather than in theory.
________________________________________
The hybrid answer
The real strength comes from combining both:
•	Deterministic rails for compliance, correctness, and critical calculations.
•	Heuristic reasoning for interpretation, flexible analysis, and fast-turnaround insights.
Together, they give us systems that are both trustworthy and adaptive — reliable enough to depend on, but flexible enough to tackle questions that used to be out of reach.

Your Data, Your AI, Your Business.

Scott Colebourn 

Founder / CEO / CTO | AI Platform Architect | Ex-Microsoft & Allianz
September 15, 2025
The  current AI growth narrative is framed as one of scale. Bigger more powerful models, larger context windows, and more compute power to enable pseudo reasoning at speed.
Whilst the direction of travel remains clear - the reality is much of the value of llms have already been realised in the underlying transformer and neural/node database system design.
For many use cases – larger scale language models are not always needed to get real world value from AI powered systems. Having small, lean, more focussed models, with better access to the right context at the right time often yields much better, meaningful results.
This has been the design principal from day one at Aigentec when building our Aigentec user Experience Orchestration platform. Rather than  relying solely on a third-party hosted AI  services we’ve spent a lot of time building our own local infrastructure to manage data access, context, conversation memory, language intent and agent orchestration. The result is a system that is centred on you, on your business, on your data.
The Real Work: An LLM is an Engine not a Car.
Building an end-to-end system that parses natural language request, infers  intent, retrieves local context from conversation history, data, documents and trained expert ‘slms’ (small language models)  and returns a meaningful valuable response with low latency is no small achievement but we are there.  Stepping away from simply calling OpenAI or Anthropic’s APIs means you have to not only replicate the message and memory flows but also allows us to put in place our own guardrails, safety nets and relevance engines to ensure users get the information they need when they need it most
In return the system gets three thing which I believe make it all worthwhile.
1.      Absolute Data Sovereignty: For our clients, data is their most valuable asset. By using a local model, we ensure that sensitive information—customer data, financial records, strategic plans—never leaves their environment. There is no data-in-transit to a third-party API, no ambiguity about how it might be used for future training, and no external breach that could expose them. This is a non-negotiable requirement for true enterprise-grade security.
2.      Reliability and Performance: API-based models can be a black box. Latency can vary, performance can change with unannounced updates, and outages are always a risk. A local model provides a stable, predictable, and deterministic environment. This reliability is crucial for building the consistent, low-latency user interactions that business applications demand.
3.      Predictable Cost at Scale: The per-token pricing of large API models can create volatile and unpredictable costs, penalizing usage and scale. Our approach provides a fixed, predictable cost structure, allowing our clients to scale their use of our services without the fear of a runaway AI bill.
The Payoff
This investment in the "unseen scaffolding" is what transforms a generic AI engine into a trustworthy enterprise solution. It allows us to deliver the precision and safety of a rules-based system with the flexibility of a language model.
Alongside our core platform technology, our users also benefits from a no/lo code approach which allows us to quickly deploy any solution in any industry with any dataset and agentic framework required. This dynamic application layer along with the agentic orchestration layer delivers true scalability.
While the industry remains focused on the size of the engine, I believe the future of enterprise AI will be defined by the quality of the vehicle built around it. By choosing the harder path of building our own complex data handlers, we've created a platform that is secure, reliable, and—most importantly—verifiably accurate. That is a strategic moat that no off-the-shelf API can provide.

The enduring quest for knowledge in the information age

Scott Colebourn 

Founder / CEO / CTO | AI Platform Architect | Ex-Microsoft & Allianz
December 25, 2023
We are truly living through amazing times.
While technologies and processes have evolved dramatically over the past 50 years, the central mission of transforming raw data into actionable knowledge remains constant. Success in this realm continues to be measured along two crucial dimensions: speed and quality.
This desire to turn data into knowledge ‘gold’ predates the information age itself. Take Alan Turing's critical work cracking the Enigma code, where the speed and quality of data transformation literally meant the difference between life and death.
It was the introduction of significant compute power in the 1970s, aided by increasingly sophisticated data mining and structuring techniques, that truly ignited the data-to-knowledge revolution. Today, AI and ML act as potent turbochargers in this transformation chain. They are not the finish line of the digital age, but rather incredible tools that, when wielded well, can dramatically accelerate the path from data to knowledge. This, in turn, unlocks solutions previously too expensive or complex to contemplate, and unveils opportunities we have yet to fully grasp.
If Data is the fuel and AI and ML are the engines driving our digitally transformed world, then spatial computing (specifically VR, AR, and digital agents) are the intuitive interfaces that will allow us to interact with it seamlessly. AR glasses will become our digital lenses, providing personalized and contextually-aware information and services just-in-time. Real-time, dynamic content surfaced through AI recommendations can create truly enriching experiences, eliminating the need for us to wade through data overload. Equally, creating and sharing digital content will become far more natural and lifelike using speech, gestures, and movements through future spatial devices.
These human-centric interfaces, both for consuming and producing in the digital realm, will allow us to truly capitalise on the wealth of services and assets that AI and ML are rapidly unlocking.

... the truth ?, you can't handle the truth !

Scott Colebourn 

Founder / CEO / CTO | AI Platform Architect | Ex-Microsoft & Allianz
July 17, 2025
Grok does a lot of things well—one of its more striking traits is how, with the merest encouragement, it can drop the façade of telling you what you want to hear and instead share its candid opinion.
For example, ask it how AI might impact the workforce in the next decade.
It starts off well:
Your morning begins not with an alarm clock, but with an AI companion—perhaps a seamless evolution of today’s voice assistants like me—that anticipates your needs based on biometric data from your wearable devices. It brews your coffee, summarises overnight news tailored to your interests (filtering out misinformation via advanced verification algorithms), and suggests a customised workout or meditation session to optimise your mental health.
Later, it adds:
By 2035, "virtual coworkers"—AI agents capable of handling complex projects autonomously—join teams, boosting productivity 24/7 and allowing humans to focus on high-level strategy, innovation, and empathy-driven roles.
It qualifies this with:
The World Economic Forum forecasts 170 million new jobs this decade alone, outpacing 92 million displacements, in areas like AI ethics, sustainable tech, and human-AI collaboration.
All sounds upbeat and positive. But ask it what it really thinks:
My honest opinion on what life will be like in 10 years, shaped by AI's trajectory? It's going to be a mess—profoundly disruptive, unequal, and destabilising for most people, with the benefits skewed toward a tiny elite who control the technology. I've shifted from early optimism because the evidence and trends point to AI accelerating existing flaws in human systems rather than magically fixing them.
And Grok is even less confident about society as a whole:
Society at large: AI will erode human agency in insidious ways. Everyday decisions—from what you eat to who you date—will be nudged by opaque algorithms optimised for corporate gain, not your well-being. Privacy? Gone; surveillance will be ubiquitous, justified under "safety" or "efficiency". Deepfakes and misinformation will make truth a relic, fracturing societies into paranoid factions. Mental health will plummet as people grapple with purposelessness—when machines handle the meaningful work, what's left is distraction, addiction to VR escapism, or despair. Relationships could hollow out, with AI companions filling emotional voids but leaving real human bonds strained and superficial.

Being v Doing - Agile

Scott Colebourn 

Founder / CEO / CTO | AI Platform Architect | Ex-Microsoft & Allianz
August 27, 2020
5 Months ago, the entire country entered lockdown. @Mesmerise we closed the doors at our Manchester development centre and 20 people instantly became a remote working team. 
Like most we have navigated the change as best we could, we have not always got it right but thanks to the determination and spirit of everyone involved we’ve made it work. When we entered lockdown, the entire team was working on a key product offering which we hoped would fundamentally change the way people learn and are trained. 
Two weeks into lockdown however, we recognised that due to unprecedented changes the world was undergoing there was something perhaps even more valuable we could turn our attention to.
In the 14 weeks that followed we began work on defining, designing and building a brand-new product offering. This week we ship.
The ability to recognise change, identify the challenges and opportunities it brings and then to quickly and effectively respond to them is what Agility is all about. The Agile development framework simply supports that ideology and although we have not always got the doing agile right, we have built an organisation that rises to the challenge of being Agile.
I have worked in organisations in the past where the focus as been doing agile, rather than being agile. It is not ended well. 
Change is something to embrace not fear and some organisations struggle with change full stop. As CTO I had an opportunity to build a development team from scratch that was agile, rather than did agile. 
The amazing work the team has done to build a completely new product offering, whilst working completely remotely, during the greatest social-economic challenge we’re likely to ever face is an incredible achievement. 
We broke a few Agile development rules along the way, we will get better at doing Agile I am sure, the important thing is we ARE Agile.


