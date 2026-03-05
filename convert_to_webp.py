#!/usr/bin/env python3
"""
EN PNG EN WebP EN
- EN
- EN（EN 85）
"""

import os
from PIL import Image

# EN
FRONTEND_DIR = "/root/.openclaw/workspace/star-office-ui/frontend"
STATIC_DIR = os.path.join(FRONTEND_DIR, "")

# EN
# EN：EN、EN
LOSSLESS_FILES = [
    "star-idle-spritesheet.png",
    "star-researching-spritesheet.png",
    "star-working-spritesheet.png",
    "sofa-busy-spritesheet.png",
    "plants-spritesheet.png",
    "posters-spritesheet.png",
    "coffee-machine-spritesheet.png",
    "serverroom-spritesheet.png"
]

# EN：EN，EN 85
LOSSY_FILES = [
    "office_bg.png",
    "sofa-idle.png",
    "desk.png"
]


def convert_to_webp(input_path, output_path, lossless=True, quality=85):
    """EN WebP"""
    try:
        img = Image.open(input_path)
        
        # EN WebP
        if lossless:
            img.save(output_path, 'WebP', lossless=True, method=6)
        else:
            img.save(output_path, 'WebP', quality=quality, method=6)
        
        # EN
        orig_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        savings = (1 - new_size / orig_size) * 100
        
        print(f"✅ {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
        print(f"   EN: {orig_size/1024:.1f}KB -> EN: {new_size/1024:.1f}KB (-{savings:.1f}%)")
        
        return True
    except Exception as e:
        print(f"❌ {os.path.basename(input_path)} EN: {e}")
        return False


def main():
    print("=" * 60)
    print("PNG → WebP EN")
    print("=" * 60)
    
    # EN
    if not os.path.exists(STATIC_DIR):
        print(f"❌ EN: {STATIC_DIR}")
        return
    
    success_count = 0
    fail_count = 0
    
    print("\n📁 EN...\n")
    
    # EN
    print("--- EN（EN）---")
    for filename in LOSSLESS_FILES:
        input_path = os.path.join(STATIC_DIR, filename)
        if not os.path.exists(input_path):
            print(f"⚠️  EN，EN: {filename}")
            continue
        
        output_path = os.path.join(STATIC_DIR, filename.replace(".png", ".webp"))
        if convert_to_webp(input_path, output_path, lossless=True):
            success_count += 1
        else:
            fail_count += 1
    
    # EN
    print("\n--- EN（EN，EN 85）---")
    for filename in LOSSY_FILES:
        input_path = os.path.join(STATIC_DIR, filename)
        if not os.path.exists(input_path):
            print(f"⚠️  EN，EN: {filename}")
            continue
        
        output_path = os.path.join(STATIC_DIR, filename.replace(".png", ".webp"))
        if convert_to_webp(input_path, output_path, lossless=False, quality=85):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"EN！EN: {success_count}, EN: {fail_count}")
    print("=" * 60)
    print("\n📝 EN:")
    print("  - PNG EN，EN")
    print("  - EN .webp EN")
    print("  - EN，EN .png EN")


if __name__ == "__main__":
    main()

