"""
GitHub Repository Data Fetcher
Fetches your public repositories and generates project documentation
"""
import requests
import json
from datetime import datetime

def fetch_github_repos(username):
    """Fetch all public repositories for a GitHub user"""
    url = f"https://api.github.com/users/{username}/repos"
    params = {
        'type': 'owner',
        'sort': 'updated',
        'per_page': 100
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching repos: {response.status_code}")
        return []

def fetch_repo_readme(username, repo_name):
    """Fetch README content for a repository"""
    url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        readme_data = response.json()
        # Get the download URL for raw content
        download_url = readme_data.get('download_url')
        if download_url:
            readme_response = requests.get(download_url)
            return readme_response.text if readme_response.status_code == 200 else ""
    return ""

def fetch_repo_languages(username, repo_name):
    """Fetch programming languages used in a repository"""
    url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    return {}

def generate_project_docs(username, output_file="github_projects.txt"):
    """Generate comprehensive project documentation from GitHub"""
    
    print(f"Fetching repositories for {username}...")
    repos = fetch_github_repos(username)
    
    if not repos:
        print("No repositories found!")
        return
    
    print(f"Found {len(repos)} repositories. Generating documentation...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"GITHUB PROJECTS - {username}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for idx, repo in enumerate(repos, 1):
            # Skip forks unless you want them
            if repo['fork']:
                continue
                
            print(f"Processing {idx}/{len(repos)}: {repo['name']}")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"PROJECT: {repo['name']}\n")
            f.write("=" * 80 + "\n\n")
            
            # Basic Info
            f.write(f"Repository: {repo['html_url']}\n")
            f.write(f"Description: {repo['description'] or 'No description provided'}\n")
            f.write(f"Created: {repo['created_at'][:10]}\n")
            f.write(f"Last Updated: {repo['updated_at'][:10]}\n")
            f.write(f"Stars: {repo['stargazers_count']} | Forks: {repo['forks_count']}\n")
            
            # Languages/Technologies
            languages = fetch_repo_languages(username, repo['name'])
            if languages:
                total_bytes = sum(languages.values())
                lang_percentages = {
                    lang: (bytes_count / total_bytes) * 100 
                    for lang, bytes_count in languages.items()
                }
                sorted_langs = sorted(lang_percentages.items(), key=lambda x: x[1], reverse=True)
                
                f.write(f"\nTechnologies Used:\n")
                for lang, percentage in sorted_langs:
                    f.write(f"  - {lang}: {percentage:.1f}%\n")
            
            # Topics/Tags
            if repo.get('topics'):
                f.write(f"\nTags: {', '.join(repo['topics'])}\n")
            
            # README Content
            readme = fetch_repo_readme(username, repo['name'])
            if readme:
                f.write(f"\nProject Details:\n")
                f.write("-" * 80 + "\n")
                # Limit README to first 2000 characters to avoid too much data
                f.write(readme[:2000])
                if len(readme) > 2000:
                    f.write("\n... (truncated)")
                f.write("\n" + "-" * 80 + "\n")
            
            f.write("\n\n")
    
    print(f"\n✅ Documentation generated: {output_file}")
    print(f"Copy this file to backend/data/ and restart your backend!")

if __name__ == "__main__":
    # Replace with your GitHub username
    GITHUB_USERNAME = "UsamaMasood12"
    
    print("GitHub Repository Data Fetcher")
    print("=" * 50)
    
    # Generate documentation
    generate_project_docs(GITHUB_USERNAME, "github_projects.txt")
    
    print("\nNext steps:")
    print("1. Copy 'github_projects.txt' to 'backend/data/'")
    print("2. Delete 'backend/vector_store' folder")
    print("3. Restart your backend server")
    print("4. Your chatbot will now know about all your GitHub projects!")
