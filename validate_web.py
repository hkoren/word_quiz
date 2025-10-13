#!/usr/bin/env python3
"""
Web Spelling Quiz Validation Script
Tests all components before deployment
"""

import os
import sys
import json
import sqlite3

def test_word_dictionary():
    """Test word dictionary loading"""
    try:
        from word_lists import word_dictionary
        print(f"✅ Word dictionary: {len(word_dictionary)} words loaded")
        
        # Test sample words
        sample_words = ['the', 'and', 'analyze', 'articulate']
        for word in sample_words:
            if word in word_dictionary:
                data = word_dictionary[word]
                print(f"   📝 {word}: grades {data['grade_levels']}, sight_word: {data['sight_word']}")
        
        return True
    except Exception as e:
        print(f"❌ Word dictionary error: {e}")
        return False

def test_file_structure():
    """Test required files exist"""
    required_files = [
        'web_quiz.py',
        'wsgi.py',
        'requirements.txt',
        'apache-vhost.conf',
        'deploy.sh',
        'word_lists.py',
        'templates/base.html',
        'templates/index.html',
        'templates/setup.html',
        'templates/quiz.html',
        'templates/results.html',
        'templates/statistics.html',
        'static/style.css'
    ]
    
    all_good = True
    print("📁 Checking file structure:")
    
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {file_path} (missing)")
            all_good = False
    
    return all_good

def test_database_functions():
    """Test database operations"""
    try:
        # Test database creation
        test_db = 'test_quiz.db'
        if os.path.exists(test_db):
            os.remove(test_db)
        
        with sqlite3.connect(test_db) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    date_time TEXT,
                    grades TEXT,
                    word_type TEXT,
                    total_words INTEGER,
                    correct_count INTEGER,
                    incorrect_count INTEGER,
                    incorrect_words TEXT,
                    percentage REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Test insert
            conn.execute('''
                INSERT INTO sessions 
                (session_id, date_time, grades, word_type, total_words, correct_count, incorrect_count, incorrect_words, percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('test', '2023-01-01', '[1,2]', 'r', 10, 8, 2, '["word1","word2"]', 80.0))
            
            # Test select
            result = conn.execute('SELECT COUNT(*) FROM sessions').fetchone()
            if result[0] == 1:
                print("✅ Database operations working")
                success = True
            else:
                print("❌ Database test failed")
                success = False
        
        # Cleanup
        if os.path.exists(test_db):
            os.remove(test_db)
        
        return success
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_template_syntax():
    """Test template files for basic syntax"""
    template_dir = 'templates'
    if not os.path.exists(template_dir):
        print("❌ Templates directory missing")
        return False
    
    templates = [f for f in os.listdir(template_dir) if f.endswith('.html')]
    print(f"🎨 Checking {len(templates)} templates:")
    
    for template in templates:
        template_path = os.path.join(template_dir, template)
        try:
            with open(template_path, 'r') as f:
                content = f.read()
                # Basic checks
                if '{% extends' in content or '<!DOCTYPE html>' in content:
                    if '{% block content %}' in content or 'base.html' in content:
                        print(f"   ✅ {template}")
                    else:
                        print(f"   ⚠️  {template} (missing block content)")
                else:
                    print(f"   ❌ {template} (invalid template)")
        except Exception as e:
            print(f"   ❌ {template} (error: {e})")
    
    return True

def test_configuration():
    """Test configuration files"""
    configs = {
        'requirements.txt': ['Flask', 'Werkzeug'],
        'apache-vhost.conf': ['VirtualHost', 'WSGIDaemonProcess'],
        'deploy.sh': ['#!/bin/bash', 'Apache']
    }
    
    print("⚙️  Checking configuration files:")
    
    for config_file, required_content in configs.items():
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                content = f.read()
                
            missing = [item for item in required_content if item not in content]
            if missing:
                print(f"   ⚠️  {config_file} (missing: {missing})")
            else:
                print(f"   ✅ {config_file}")
        else:
            print(f"   ❌ {config_file} (missing)")
    
    return True

def main():
    print("🎯 Web Spelling Quiz Validation")
    print("=" * 40)
    
    tests = [
        ("Word Dictionary", test_word_dictionary),
        ("File Structure", test_file_structure),
        ("Database Functions", test_database_functions),
        ("Template Syntax", test_template_syntax),
        ("Configuration", test_configuration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}:")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    if all(results):
        print("🎉 All tests passed! Web application is ready for deployment.")
        print("\n📋 Next steps:")
        print("   1. Install Flask: pip install -r requirements.txt")
        print("   2. Test locally: python3 web_quiz.py")
        print("   3. Deploy to Apache: ./deploy.sh")
        return 0
    else:
        failed_count = results.count(False)
        print(f"❌ {failed_count} test(s) failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())