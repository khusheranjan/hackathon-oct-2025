"""
Example Usage Scripts for AI Educational Video Generator
"""

import os
from video_generator import EducationalVideoGenerator
from advanced_generator import AdvancedVideoGenerator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def example_1_pythagorean_theorem():
    """
    Example 1: Simple mathematical concept
    """
    print("=" * 60)
    print("EXAMPLE 1: Pythagorean Theorem")
    print("=" * 60)

    # API keys will be loaded from .env automatically
    generator = EducationalVideoGenerator()
    
    description = """
    Explain the Pythagorean theorem (a² + b² = c²) visually.
    Start with a right triangle, label the sides a, b, and c.
    Then show squares drawn on each side.
    Demonstrate that the area of squares on the two legs equals
    the area of the square on the hypotenuse.
    Include a numerical example: a=3, b=4, c=5.
    Use colors: blue for side a, green for side b, red for hypotenuse c.
    """
    
    results = generator.generate_video(description, "pythagorean_theorem")
    print(f"\n✅ Video created: {results['final_video']}")


def example_2_photosynthesis():
    """
    Example 2: Biology concept with multiple steps
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Photosynthesis Process")
    print("=" * 60)

    # API keys will be loaded from .env automatically
    generator = AdvancedVideoGenerator()
    
    description = """
    Explain photosynthesis in plants step by step:
    1. Show sunlight rays hitting a green leaf
    2. Zoom into a chloroplast inside the leaf
    3. Show CO2 and H2O molecules entering
    4. Display the chemical equation: 6CO2 + 6H2O → C6H12O6 + 6O2
    5. Show glucose and oxygen being produced
    6. Emphasize this is how plants make food and produce oxygen
    
    Use green theme for the leaf, yellow for sunlight, blue for water,
    and red for oxygen. Keep it engaging for middle school students.
    """
    
    results = generator.generate_video(
        description,
        "photosynthesis_explained",
        add_subtitles=True
    )
    print(f"\n✅ Video created: {results['final_video']}")


def example_3_compound_interest():
    """
    Example 3: Financial concept with graphs
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Compound Interest")
    print("=" * 60)

    # API keys will be loaded from .env automatically
    generator = EducationalVideoGenerator()
    
    description = """
    Teach compound interest to high school students.
    
    Start by showing the formula: A = P(1 + r/n)^(nt)
    Explain each variable:
    - A = final amount
    - P = principal (initial investment)
    - r = annual interest rate
    - n = times compounded per year
    - t = number of years
    
    Then show a concrete example:
    - Initial investment: $1,000
    - Interest rate: 5% per year
    - Compounded annually
    - Time: 10 years
    
    Calculate and show the growth with an animated graph showing
    the money growing over time. Compare it to simple interest
    to show the "interest on interest" effect.
    
    Use green for growing money, blue for the principal amount.
    """
    
    results = generator.generate_video(description, "compound_interest")
    print(f"\n✅ Video created: {results['final_video']}")


def example_4_newtons_laws():
    """
    Example 4: Physics with real-world examples
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Newton's Laws of Motion")
    print("=" * 60)

    # API keys will be loaded from .env automatically
    generator = AdvancedVideoGenerator()
    
    description = """
    Explain Newton's Three Laws of Motion with visual demonstrations:
    
    Law 1 (Inertia):
    - Show a ball at rest staying at rest
    - Show a ball in motion continuing to move
    - Example: Hockey puck sliding on ice
    
    Law 2 (F = ma):
    - Display the equation F = ma
    - Show how more force creates more acceleration
    - Show how more mass needs more force
    - Example: Pushing an empty vs. full shopping cart
    
    Law 3 (Action-Reaction):
    - Show equal and opposite forces
    - Example: Rocket launching (gases push down, rocket goes up)
    - Example: Walking (foot pushes ground back, body moves forward)
    
    Use dynamic animations with arrows for forces. Make it engaging
    for high school physics students.
    """
    
    results = generator.generate_video(
        description,
        "newtons_laws",
        add_subtitles=True
    )
    print(f"\n✅ Video created: {results['final_video']}")


def example_5_binary_numbers():
    """
    Example 5: Computer Science concept
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Binary Number System")
    print("=" * 60)

    # API keys will be loaded from .env automatically
    generator = EducationalVideoGenerator()
    
    description = """
    Introduce the binary number system for beginners:
    
    1. Explain that computers only understand 0s and 1s
    2. Show place values in binary: 1, 2, 4, 8, 16, 32, 64, 128
    3. Compare to decimal place values: 1, 10, 100, 1000
    4. Convert decimal 13 to binary step by step:
       - 13 = 8 + 4 + 1
       - 13 = 1×8 + 1×4 + 0×2 + 1×1
       - 13 = 1101 in binary
    5. Show a few more examples: 5, 10, 25
    6. Mention that this is the foundation of all computing
    
    Use on/off light bulbs to represent 1s and 0s. Make it colorful
    and accessible for middle school students learning computer science.
    """
    
    results = generator.generate_video(description, "binary_numbers")
    print(f"\n✅ Video created: {results['final_video']}")


def example_6_water_cycle():
    """
    Example 6: Earth Science with continuous process
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 6: The Water Cycle")
    print("=" * 60)

    # API keys will be loaded from .env automatically
    generator = AdvancedVideoGenerator()
    
    description = """
    Explain the water cycle as a continuous process:
    
    1. Evaporation:
       - Sun heats water in oceans, lakes, and rivers
       - Water turns into vapor and rises
    
    2. Condensation:
       - Water vapor cools high in the atmosphere
       - Forms clouds made of tiny water droplets
    
    3. Precipitation:
       - Water droplets combine and become heavy
       - Falls as rain, snow, or hail
    
    4. Collection:
       - Water flows into streams, rivers, oceans
       - Soaks into the ground (groundwater)
       - The cycle repeats
    
    Show this as a continuous circular animation. Use blue for water,
    yellow for the sun, white/gray for clouds. Make it flow smoothly
    to show the cycle nature. Target elementary school students.
    """
    
    results = generator.generate_video(
        description,
        "water_cycle",
        add_subtitles=True
    )
    print(f"\n✅ Video created: {results['final_video']}")


def run_all_examples():
    """
    Run all examples (this will take a while!)
    """
    print("\n🎬 Running all examples...")
    print("⏱️  This will take approximately 15-30 minutes\n")
    
    examples = [
        example_1_pythagorean_theorem,
        example_2_photosynthesis,
        example_3_compound_interest,
        example_4_newtons_laws,
        example_5_binary_numbers,
        example_6_water_cycle
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n\n{'='*60}")
        print(f"Running Example {i}/{len(examples)}")
        print(f"{'='*60}")
        
        try:
            example()
        except Exception as e:
            print(f"\n❌ Error in example {i}: {e}")
            continue
    
    print("\n\n🎉 All examples completed!")
    print("📁 Check the 'outputs' directory for generated videos")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        
        examples = {
            "1": example_1_pythagorean_theorem,
            "2": example_2_photosynthesis,
            "3": example_3_compound_interest,
            "4": example_4_newtons_laws,
            "5": example_5_binary_numbers,
            "6": example_6_water_cycle,
            "all": run_all_examples
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Unknown example: {example_num}")
            print("Usage: python examples.py [1-6|all]")
    else:
        print("AI Educational Video Generator - Examples")
        print("\nAvailable examples:")
        print("  1. Pythagorean Theorem")
        print("  2. Photosynthesis")
        print("  3. Compound Interest")
        print("  4. Newton's Laws of Motion")
        print("  5. Binary Number System")
        print("  6. Water Cycle")
        print("  all. Run all examples")
        print("\nUsage: python examples.py [1-6|all]")
