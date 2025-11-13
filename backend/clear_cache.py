#!/usr/bin/env python
"""
Clear all caches for fresh testing
"""
import os
import glob

def clear_caches():
    """Clear all cache files"""
    cache_files = [
        'response_cache.json',
        'analytics.json',
        '*.cache',
        '*.pkl'
    ]
    
    cleared = 0
    for pattern in cache_files:
        for file in glob.glob(pattern):
            try:
                os.remove(file)
                print(f"✅ Deleted: {file}")
                cleared += 1
            except Exception as e:
                print(f"❌ Error deleting {file}: {e}")
    
    if cleared == 0:
        print("✅ No cache files found (already clean)")
    else:
        print(f"\n✅ Cleared {cleared} cache file(s)")
    
    print("\n🚀 Ready for fresh testing!")
    print("Run: python -m app.main")

if __name__ == "__main__":
    clear_caches()
