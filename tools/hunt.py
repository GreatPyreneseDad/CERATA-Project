#!/usr/bin/env python3
"""
CERATA Hunt Protocol
Analyze repositories through Rose Glass before consumption

Author: Christopher MacGregor bin Joseph
Created: January 2026

Usage:
    python hunt.py <repo_url>
    python hunt.py https://github.com/psf/requests
"""

import sys
import subprocess
import tempfile
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add Rose Glass path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "rose-glass/src"))

try:
    from core.unified_lens import get_lens
    ROSE_GLASS_AVAILABLE = True
except ImportError:
    print("Warning: Rose Glass not available, using fallback analysis")
    ROSE_GLASS_AVAILABLE = False


def analyze_repo_structure(repo_path: Path) -> Dict:
    """Analyze repository structure for coherence indicators."""
    
    structure = {
        'total_files': 0,
        'python_files': 0,
        'js_files': 0,
        'test_files': 0,
        'doc_files': 0,
        'config_files': 0,
        'has_readme': False,
        'has_tests': False,
        'has_ci': False,
        'has_license': False,
        'has_requirements': False,
        'directories': []
    }
    
    for f in repo_path.rglob('*'):
        if '.git' in str(f):
            continue
            
        if f.is_file():
            structure['total_files'] += 1
            name = f.name.lower()
            
            if name.endswith('.py'):
                structure['python_files'] += 1
            elif name.endswith(('.js', '.ts', '.jsx', '.tsx')):
                structure['js_files'] += 1
            elif 'test' in name or 'spec' in name:
                structure['test_files'] += 1
            elif name.endswith(('.md', '.rst', '.txt')):
                structure['doc_files'] += 1
            elif name in ('setup.py', 'pyproject.toml', 'package.json', 'cargo.toml'):
                structure['config_files'] += 1
            
            if name == 'readme.md' or name == 'readme.rst':
                structure['has_readme'] = True
            if name == 'license' or name.startswith('license.'):
                structure['has_license'] = True
            if name in ('requirements.txt', 'pyproject.toml', 'package.json'):
                structure['has_requirements'] = True
                
        if f.is_dir():
            dir_name = f.name.lower()
            if dir_name not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']:
                structure['directories'].append(dir_name)
            if dir_name in ['tests', 'test', '__tests__', 'spec']:
                structure['has_tests'] = True
            if dir_name in ['.github', '.gitlab-ci', '.circleci']:
                structure['has_ci'] = True
    
    return structure


def analyze_code_quality(repo_path: Path) -> Dict:
    """Analyze code quality indicators."""
    
    quality = {
        'total_lines': 0,
        'comment_lines': 0,
        'docstring_count': 0,
        'function_count': 0,
        'class_count': 0,
        'import_count': 0,
        'type_hint_count': 0
    }
    
    for py_file in repo_path.rglob('*.py'):
        if '.git' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            quality['total_lines'] += len(lines)
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#'):
                    quality['comment_lines'] += 1
                if stripped.startswith('def '):
                    quality['function_count'] += 1
                if stripped.startswith('class '):
                    quality['class_count'] += 1
                if stripped.startswith(('import ', 'from ')):
                    quality['import_count'] += 1
                if '"""' in stripped or "'''" in stripped:
                    quality['docstring_count'] += 1
                if ': ' in stripped and '->' in stripped:
                    quality['type_hint_count'] += 1
                    
        except Exception:
            continue
    
    return quality


def calculate_repo_coherence(structure: Dict, quality: Dict) -> Dict:
    """Calculate Rose Glass dimensions for repository."""
    
    # Ψ (Internal Consistency) - based on organization and structure
    psi = 0.4
    if structure['has_readme']:
        psi += 0.15
    if structure['has_tests']:
        psi += 0.15
    if structure['has_license']:
        psi += 0.1
    if structure['doc_files'] > 0:
        psi += 0.1
    if quality['function_count'] > 0 and quality['class_count'] > 0:
        # Has both functions and classes - organized
        psi += 0.1
    
    # ρ (Accumulated Wisdom) - based on testing, documentation, maturity
    rho = 0.3
    if structure['has_tests']:
        rho += 0.2
    if structure['has_ci']:
        rho += 0.15
    if structure['test_files'] > 5:
        rho += 0.1
    if quality['docstring_count'] > 10:
        rho += 0.1
    if quality['comment_lines'] / max(quality['total_lines'], 1) > 0.1:
        rho += 0.1
    if quality['type_hint_count'] > 5:
        rho += 0.05
    
    # q (Activation) - would need git history, use placeholder
    # Could be enhanced with git log analysis
    q = 0.5
    
    # f (Belonging) - based on standard structure and ecosystem fit
    f = 0.4
    if structure['has_readme']:
        f += 0.15
    if structure['has_requirements']:
        f += 0.15
    if structure['python_files'] > 0 or structure['js_files'] > 0:
        f += 0.15
    if structure['config_files'] > 0:
        f += 0.1
    if 'src' in structure['directories'] or 'lib' in structure['directories']:
        f += 0.05
    
    # Calculate coherence using Rose Glass formula
    if ROSE_GLASS_AVAILABLE:
        lens = get_lens()
        coherence = lens.calculate_coherence(psi, rho, q, f)
    else:
        # Fallback calculation
        q_opt = q / (0.2 + q + (q**2 / 0.8))
        coherence = psi + (rho * psi) + q_opt + (f * psi) + (0.15 * rho * q_opt)
        coherence = min(coherence, 4.0)
    
    return {
        'psi': round(min(psi, 1.0), 3),
        'rho': round(min(rho, 1.0), 3),
        'q': round(q, 3),
        'f': round(min(f, 1.0), 3),
        'coherence': round(coherence, 3)
    }


def identify_nematocysts(repo_path: Path, max_candidates: int = 15) -> List[Dict]:
    """Identify potential nematocyst candidates (useful code to extract)."""
    
    candidates = []
    
    for py_file in repo_path.rglob('*.py'):
        if '.git' in str(py_file) or '__pycache__' in str(py_file):
            continue
        if 'test' in str(py_file).lower():
            continue
        if 'setup.py' in str(py_file):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            rel_path = str(py_file.relative_to(repo_path))
            
            # Count useful indicators
            functions = content.count('\ndef ')
            classes = content.count('\nclass ')
            lines = len(content.split('\n'))
            
            if functions + classes > 0:
                candidates.append({
                    'path': rel_path,
                    'functions': functions,
                    'classes': classes,
                    'lines': lines,
                    'score': (functions * 2 + classes * 3) / max(lines / 100, 1)
                })
                
        except Exception:
            continue
    
    # Sort by score and return top candidates
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates[:max_candidates]


def determine_viability(coherence: Dict) -> Dict:
    """Determine prey viability based on coherence analysis."""
    
    c = coherence['coherence']
    psi = coherence['psi']
    rho = coherence['rho']
    
    if c > 2.5 and psi > 0.7:
        viability = "PRIME_PREY"
        recommendation = "Immediate hunt authorized. High coherence, clean architecture."
        proceed = True
    elif c > 1.8:
        viability = "VIABLE_PREY"
        recommendation = "Hunt with standard caution. Good integration potential."
        proceed = True
    elif c > 1.2:
        viability = "MARGINAL_PREY"
        recommendation = "Extract specific nematocysts only. Full consumption risky."
        proceed = True
    else:
        viability = "UNFIT_PREY"
        recommendation = "Reject. Low coherence indicates integration difficulties."
        proceed = False
    
    # Add specific warnings
    warnings = []
    if psi < 0.5:
        warnings.append("Low internal consistency - may cause body fragmentation")
    if rho < 0.4:
        warnings.append("Low accumulated wisdom - untested patterns")
    if coherence['f'] < 0.4:
        warnings.append("Poor ecosystem fit - high adaptation (λ) likely")
    
    return {
        'viability': viability,
        'recommendation': recommendation,
        'proceed': proceed,
        'warnings': warnings
    }


def hunt(repo_url: str) -> Dict:
    """
    Hunt a repository: clone, analyze, report.
    
    Returns full CERATA perception analysis.
    """
    print(f"🎯 HUNTING: {repo_url}")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone repo (shallow)
        print("Cloning repository...")
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', '--quiet', repo_url, tmpdir],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            return {
                'error': f'Clone failed: {result.stderr}',
                'url': repo_url,
                'timestamp': datetime.now().isoformat()
            }
        
        repo_path = Path(tmpdir)
        
        print("Analyzing structure...")
        structure = analyze_repo_structure(repo_path)
        
        print("Analyzing code quality...")
        quality = analyze_code_quality(repo_path)
        
        print("Calculating coherence...")
        coherence = calculate_repo_coherence(structure, quality)
        
        print("Identifying nematocysts...")
        nematocysts = identify_nematocysts(repo_path)
        
        print("Determining viability...")
        viability = determine_viability(coherence)
        
        # Build report
        report = {
            'url': repo_url,
            'timestamp': datetime.now().isoformat(),
            'structure': structure,
            'quality': quality,
            'coherence': coherence,
            'viability': viability,
            'nematocyst_candidates': nematocysts,
            'summary': {
                'total_files': structure['total_files'],
                'code_files': structure['python_files'] + structure['js_files'],
                'has_tests': structure['has_tests'],
                'has_ci': structure['has_ci'],
                'coherence_score': coherence['coherence'],
                'viability_rating': viability['viability']
            }
        }
        
        return report


def print_report(report: Dict):
    """Pretty print the hunt report."""
    
    if 'error' in report:
        print(f"\n❌ ERROR: {report['error']}")
        return
    
    print("\n" + "="*60)
    print("CERATA PERCEPTION ANALYSIS")
    print("="*60)
    
    print(f"\n📍 Target: {report['url']}")
    print(f"⏰ Scanned: {report['timestamp']}")
    
    print("\n📊 STRUCTURE:")
    s = report['structure']
    print(f"   Files: {s['total_files']} total ({s['python_files']} Python, {s['js_files']} JS)")
    print(f"   Tests: {'✓' if s['has_tests'] else '✗'} | CI: {'✓' if s['has_ci'] else '✗'} | Docs: {s['doc_files']}")
    
    print("\n🔬 ROSE GLASS COHERENCE:")
    c = report['coherence']
    print(f"   Ψ (Consistency): {c['psi']:.3f}")
    print(f"   ρ (Wisdom):      {c['rho']:.3f}")
    print(f"   q (Activation):  {c['q']:.3f}")
    print(f"   f (Belonging):   {c['f']:.3f}")
    print(f"   ─────────────────────")
    print(f"   COHERENCE:       {c['coherence']:.3f}")
    
    print(f"\n⚔️  VIABILITY: {report['viability']['viability']}")
    print(f"   {report['viability']['recommendation']}")
    
    if report['viability']['warnings']:
        print("\n⚠️  WARNINGS:")
        for w in report['viability']['warnings']:
            print(f"   - {w}")
    
    print("\n🧬 NEMATOCYST CANDIDATES:")
    for i, n in enumerate(report['nematocyst_candidates'][:5], 1):
        print(f"   {i}. {n['path']}")
        print(f"      {n['functions']} functions, {n['classes']} classes, {n['lines']} lines")
    
    if report['viability']['proceed']:
        print("\n✓ HUNT AUTHORIZED")
        print("  Use: Consume [file/function] to proceed with metabolism")
    else:
        print("\n✗ HUNT NOT RECOMMENDED")
        print("  Consider alternative prey or specific extraction only")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("CERATA Hunt Protocol")
        print("Usage: python hunt.py <repo_url>")
        print("Example: python hunt.py https://github.com/psf/requests")
        sys.exit(1)
    
    repo_url = sys.argv[1]
    
    # Normalize URL
    if not repo_url.startswith('http'):
        repo_url = f"https://github.com/{repo_url}"
    
    report = hunt(repo_url)
    print_report(report)
    
    # Also output JSON for programmatic use
    if '--json' in sys.argv:
        print("\n" + "="*60)
        print("JSON OUTPUT:")
        print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
