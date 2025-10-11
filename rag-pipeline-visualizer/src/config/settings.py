"""Configuration settings for RAG Visualizer"""

# Model options
MODEL_OPTIONS = {
    "all-MiniLM-L6-v2 (Fast)": "sentence-transformers/all-MiniLM-L6-v2",
    "all-mpnet-base-v2 (Accurate)": "sentence-transformers/all-mpnet-base-v2",
    "paraphrase-multilingual (Multilingual)": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
}

# Sample texts
SAMPLE_TEXTS = {
    "AI & Machine Learning": """
        Artificial intelligence and machine learning are fundamentally transforming how we interact with technology in the modern world. 
        These revolutionary technologies enable computers to learn from data and make intelligent decisions without explicit programming.
        
        Deep learning models, inspired by the human brain's neural networks, have achieved remarkable breakthroughs in recent years. 
        These models consist of multiple layers of artificial neurons that process information hierarchically, extracting increasingly 
        complex features from raw data. Convolutional neural networks excel at image recognition tasks, while recurrent neural networks 
        are particularly effective for sequential data like text and time series.
        
        Natural language processing represents one of the most exciting frontiers in AI research. Modern language models can understand 
        context, generate human-like text, translate between languages, and even engage in meaningful conversations. Transformer 
        architectures, introduced in 2017, have revolutionized NLP by enabling models to process entire sequences simultaneously 
        rather than word by word. This breakthrough has led to powerful models like GPT, BERT, and their successors.
        
        Computer vision has made tremendous strides, enabling machines to interpret and understand visual information from the world. 
        Applications range from facial recognition and autonomous vehicles to medical image analysis and quality control in manufacturing. 
        Object detection algorithms can identify and locate multiple objects within images in real-time, while semantic segmentation 
        techniques can classify every pixel in an image.
        
        Reinforcement learning teaches agents to make sequences of decisions by learning from interaction with their environment. 
        The agent receives rewards or penalties based on its actions and learns to maximize cumulative reward over time. This approach 
        has achieved superhuman performance in games like Chess, Go, and complex video games. Real-world applications include robotics, 
        autonomous systems, and resource optimization.
        
        Machine learning algorithms fall into three main categories: supervised learning uses labeled data to train models, unsupervised 
        learning finds patterns in unlabeled data, and semi-supervised learning combines both approaches. Each paradigm has its strengths 
        and is suited to different types of problems. Feature engineering and data preprocessing remain crucial steps in building 
        effective machine learning systems.
        
        The ethical implications of AI deployment are increasingly important considerations. Issues of bias in training data, privacy 
        concerns, transparency in decision-making, and the potential impact on employment require careful attention. Responsible AI 
        development emphasizes fairness, accountability, and transparency. As these technologies become more powerful and widespread, 
        establishing ethical guidelines and regulatory frameworks becomes essential for ensuring AI benefits humanity as a whole.
    """,
    "Climate & Environment": """
        Climate change represents one of the most pressing challenges facing humanity in the 21st century, affecting ecosystems, 
        weather patterns, and human societies across the globe. Rising global temperatures, driven primarily by greenhouse gas 
        emissions from human activities, are causing widespread environmental disruptions.
        
        The scientific consensus is clear: human activities, particularly the burning of fossil fuels and deforestation, have 
        significantly increased atmospheric concentrations of carbon dioxide, methane, and other greenhouse gases. These gases trap 
        heat in the atmosphere, leading to global warming and associated climate changes. Temperature records show that the past 
        decade has been the warmest on record, with each successive year often breaking previous heat records.
        
        Renewable energy sources are becoming increasingly vital in the transition away from fossil fuels. Solar power technology 
        has advanced dramatically, with photovoltaic cell efficiency improving and costs dropping significantly over the past decade. 
        Wind energy, both onshore and offshore, provides clean electricity generation with minimal environmental impact. Hydroelectric 
        power, geothermal energy, and emerging technologies like tidal and wave energy contribute to a diversified renewable energy 
        portfolio. Energy storage solutions, particularly advanced battery technologies, are crucial for managing the intermittent 
        nature of renewable sources.
        
        Deforestation continues to be a major environmental concern, contributing substantially to carbon emissions and biodiversity 
        loss. Forests act as critical carbon sinks, absorbing CO2 from the atmosphere. When forests are cleared, this stored carbon 
        is released, and the capacity for future carbon absorption is lost. The Amazon rainforest, often called the "lungs of the Earth," 
        faces unprecedented threats from logging, agricultural expansion, and wildfires. Similar concerns affect forests in Southeast 
        Asia, Central Africa, and other regions.
        
        Ocean acidification, often called climate change's "evil twin," poses severe threats to marine ecosystems. As atmospheric CO2 
        concentrations increase, oceans absorb more carbon dioxide, which reacts with seawater to form carbonic acid. This process 
        lowers ocean pH, making waters more acidic. The consequences are particularly severe for organisms with calcium carbonate 
        shells or skeletons, including corals, mollusks, and certain plankton species. Coral reef ecosystems, which support 
        approximately 25% of all marine species, are especially vulnerable to both warming and acidification.
        
        Sustainable practices across agriculture, industry, and daily life are essential for environmental conservation and climate 
        mitigation. Regenerative agriculture techniques can restore soil health while sequestering carbon. Circular economy principles 
        minimize waste by designing products for reuse, repair, and recycling. Green building practices reduce energy consumption 
        and environmental impact in construction. Individual actions, while modest in isolation, collectively contribute to broader 
        sustainability goals.
        
        Biodiversity conservation is intrinsically linked to climate action. Ecosystems with high biodiversity tend to be more 
        resilient to environmental changes and more effective at providing ecosystem services like carbon sequestration, water 
        purification, and pollination. Protected areas, habitat restoration projects, and wildlife corridors help preserve species 
        and ecosystems. International cooperation through agreements like the Paris Climate Accord and Convention on Biological 
        Diversity demonstrates global commitment to addressing these interconnected challenges.
    """,
    "Space Exploration": """
        Space exploration has captivated human imagination for generations, leading to incredible scientific discoveries and 
        technological innovations that have expanded our understanding of the cosmos. From the first artificial satellites to 
        ambitious plans for human settlements on other planets, our journey into space continues to push the boundaries of what's possible.
        
        The history of space exploration began in earnest during the mid-20th century with the Space Race between the United States 
        and Soviet Union. Landmark achievements included Sputnik 1, the first artificial satellite, Yuri Gagarin's historic first 
        human spaceflight, and the Apollo 11 moon landing in 1969, when Neil Armstrong and Buzz Aldrin became the first humans to 
        walk on the lunar surface. These achievements demonstrated humanity's capability to venture beyond Earth and laid the 
        foundation for modern space programs.
        
        Mars exploration represents one of the most active areas of current space research. Multiple rovers, including Curiosity, 
        Perseverance, and China's Zhurong, are currently exploring the Martian surface. These robotic explorers search for signs of 
        ancient microbial life, study the planet's geology and climate, and prepare for future human missions. Perseverance's 
        companion, the Ingenuity helicopter, demonstrated powered flight in Mars's thin atmosphere, opening new possibilities for 
        aerial exploration. Sample return missions aim to bring Martian rocks and soil back to Earth for detailed laboratory analysis.
        
        The James Webb Space Telescope, launched in December 2021, represents a quantum leap in our ability to observe the universe. 
        This powerful infrared observatory can peer through cosmic dust clouds to see the first galaxies that formed after the Big Bang, 
        study the formation of stars and planetary systems, and analyze the atmospheres of exoplanets in unprecedented detail. Early 
        observations have already revealed stunning images of distant galaxies, nebulae, and exoplanet atmospheres, promising 
        revolutionary discoveries about cosmic origins and the potential for life beyond Earth.
        
        The search for exoplanets—planets orbiting stars beyond our solar system—has exploded in recent decades. Missions like Kepler 
        and TESS have discovered thousands of exoplanets, revealing that planetary systems are common throughout the galaxy. Some 
        exoplanets orbit within their star's habitable zone, where conditions might support liquid water and potentially life. 
        Advanced spectroscopic techniques allow scientists to analyze exoplanet atmospheres, searching for biosignatures that might 
        indicate biological activity.
        
        Private space companies are revolutionizing access to space through innovation and competition. SpaceX's development of 
        reusable rocket technology with the Falcon 9 and Starship dramatically reduces launch costs, making space more accessible. 
        Blue Origin focuses on suborbital tourism and developing heavy-lift launch vehicles. Other companies are developing small 
        satellite launchers, space habitats, and lunar landers. This commercial space industry accelerates innovation and enables 
        new applications in communications, Earth observation, and scientific research.
        
        International space stations serve as unique laboratories for scientific research in microgravity. The International Space 
        Station, a collaborative project involving NASA, Roscosmos, ESA, JAXA, and CSA, has been continuously occupied since 2000. 
        Research conducted aboard the ISS spans biology, physics, astronomy, and materials science. Experiments investigate how 
        microgravity affects human physiology, test new materials and manufacturing processes, and study fundamental physical phenomena. 
        China's Tiangong space station expands international presence in low Earth orbit.
        
        Future space exploration plans are increasingly ambitious. NASA's Artemis program aims to return humans to the Moon and 
        establish a sustainable presence there, serving as a stepping stone for eventual Mars missions. Space agencies and private 
        companies are developing technologies for long-duration spaceflight, including advanced propulsion systems, radiation shielding, 
        and life support systems. Mining asteroids for resources, building lunar bases, and establishing Mars colonies transition 
        from science fiction to serious engineering challenges. The coming decades promise to be the most exciting era in space 
        exploration history.
    """
}

# Default values
DEFAULT_CHUNK_SIZE = 100
DEFAULT_OVERLAP = 20
DEFAULT_COLLECTION_NAME = "rag_embeddings"
DEFAULT_N_RESULTS = 3
DEFAULT_REDUCTION_METHOD = "PCA"

