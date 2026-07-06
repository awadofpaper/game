"""
Batch fix Unicode symbols in all test files
Replaces ✅ → [OK], ❌ → [FAIL], ⚠️ → [WARN]
"""
import os
import glob

def fix_unicode_in_file(filepath):
    """Replace Unicode symbols with ASCII in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Replace Unicode symbols
        content = content.replace('✅', '[OK]')
        content = content.replace('❌', '[FAIL]')
        content = content.replace('⚠️', '[WARN]')
        content = content.replace('⚠', '[WARN]')  # Without variation selector
        
        # Replace emojis with ASCII
        content = content.replace('🎉', '!')
        content = content.replace('📊', '[STATS]')
        content = content.replace('⚡', '[EXCELLENT]')
        content = content.replace('🎮', '')
        content = content.replace('🐛', '[BUG]')
        content = content.replace('🚀', '[FAST]')
        content = content.replace('💎', '[RARE]')
        content = content.replace('🔥', '[HOT]')
        
        # Only write if changes were made
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"[FAIL] Error processing {filepath}: {e}")
        return False

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = glob.glob(os.path.join(base_dir, 'test_*.py'))
    
    print("=" * 70)
    print("UNICODE FIX SCRIPT")
    print("=" * 70)
    print(f"\nFound {len(test_files)} test files")
    print("\nProcessing files...")
    print("-" * 70)
    
    fixed_count = 0
    for filepath in sorted(test_files):
        filename = os.path.basename(filepath)
        if fix_unicode_in_file(filepath):
            print(f"[OK] Fixed: {filename}")
            fixed_count += 1
        else:
            print(f"[SKIP] No changes: {filename}")
    
    print("-" * 70)
    print(f"\n[OK] Fixed {fixed_count} of {len(test_files)} files")
    print("=" * 70)

if __name__ == '__main__':
    main()
