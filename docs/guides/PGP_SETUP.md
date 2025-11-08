# 🔐 PGP Key Setup for FastProxy Releases

Complete guide to creating and managing PGP keys for signing releases and commits.

## 📋 Table of Contents

- [Why Use PGP Keys?](#why-use-pgp-keys)
- [Installation](#installation)
- [Creating Your PGP Key](#creating-your-pgp-key)
- [Configure Git](#configure-git)
- [Sign Commits](#sign-commits)
- [Sign Releases](#sign-releases)
- [Publish Your Public Key](#publish-your-public-key)
- [Backup Your Keys](#backup-your-keys)

## Why Use PGP Keys?

PGP (Pretty Good Privacy) keys provide:
- ✅ **Authenticity**: Verify releases are from you
- ✅ **Integrity**: Ensure code hasn't been tampered with
- ✅ **Trust**: Build confidence in your releases
- ✅ **Security**: Industry standard for open source

## Installation

### macOS

```bash
# Using Homebrew
brew install gnupg

# Or using MacGPG
# Download from: https://gpgtools.org/

# Verify installation
gpg --version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install gnupg

# Verify installation
gpg --version
```

### Linux (CentOS/RHEL)

```bash
sudo yum install gnupg2

# Verify installation
gpg --version
```

### Windows

```bash
# Download from: https://www.gnupg.org/download/
# Or use: https://gpg4win.org/

# Verify installation
gpg --version
```

## Creating Your PGP Key

### Step 1: Generate Key

```bash
# Start key generation
gpg --full-generate-key
```

**Follow the prompts:**

1. **Key type**: Choose `(1) RSA and RSA (default)`
2. **Key size**: Choose `4096` (maximum security)
3. **Expiration**: Choose `0 = key does not expire` or set expiration (e.g., `2y` for 2 years)
4. **Confirm**: Type `y`
5. **Real name**: Your full name (e.g., "Rajesh Chandran")
6. **Email**: Your GitHub email (e.g., "your@email.com")
7. **Comment**: Optional (e.g., "FastProxy Release Signing")
8. **Passphrase**: Choose a strong passphrase (IMPORTANT!)

### Step 2: List Your Keys

```bash
# List public keys
gpg --list-keys

# Output example:
# pub   rsa4096 2025-01-08 [SC]
#       1234567890ABCDEF1234567890ABCDEF12345678
# uid           [ultimate] Your Name <your@email.com>
# sub   rsa4096 2025-01-08 [E]
```

The long string is your **KEY_ID** - you'll need this!

### Step 3: Export Public Key

```bash
# Replace KEY_ID with your actual key ID
gpg --armor --export YOUR_KEY_ID > pgp-public-key.asc

# View your public key
cat pgp-public-key.asc
```

## Configure Git

### Set Up Git to Use Your Key

```bash
# Get your key ID (use the long format)
gpg --list-secret-keys --keyid-format=long

# Example output:
# sec   rsa4096/ABC123DEF456 2025-01-08
#                ^^^^^^^^^^^^ This is your KEY_ID

# Configure Git with your key
git config --global user.signingkey YOUR_KEY_ID

# Enable commit signing by default
git config --global commit.gpgsign true

# Enable tag signing by default
git config --global tag.gpgsign true

# Configure GPG program (if needed)
git config --global gpg.program gpg
```

### Add to Your Git Config

```bash
# Add your name and email (if not already set)
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Verify configuration
git config --global --list | grep -E "user|signing|gpg"
```

## Sign Commits

### Manually Sign a Commit

```bash
# Sign a single commit
git commit -S -m "Your commit message"

# The -S flag signs the commit
```

### Auto-Sign All Commits

```bash
# Already configured above with:
git config --global commit.gpgsign true

# Now all commits are automatically signed
git commit -m "This will be automatically signed"
```

### Verify Signed Commits

```bash
# View commit signatures
git log --show-signature

# Or
git log --pretty="format:%h %G? %aN  %s"
# G? shows: G=good signature, B=bad signature, N=no signature
```

## Sign Releases

### Sign a Git Tag

```bash
# Create a signed tag for release
git tag -s v2.0.0 -m "Version 2.0.0 - Complete Management WebApp"

# Push the tag
git push origin v2.0.0

# Verify the tag signature
git tag -v v2.0.0
```

### Sign Release Archives

```bash
# Create release archive
git archive --format=tar.gz --prefix=fastproxy-2.0.0/ v2.0.0 > fastproxy-2.0.0.tar.gz

# Sign the archive
gpg --armor --detach-sign fastproxy-2.0.0.tar.gz

# This creates: fastproxy-2.0.0.tar.gz.asc

# Users can verify with:
# gpg --verify fastproxy-2.0.0.tar.gz.asc fastproxy-2.0.0.tar.gz
```

### Sign Docker Images

```bash
# Install cosign (for container signing)
brew install cosign

# Sign Docker image
cosign sign --key cosign.key username/fastproxy:2.0.0

# Users can verify with:
# cosign verify --key cosign.pub username/fastproxy:2.0.0
```

## Publish Your Public Key

### 1. Upload to Key Servers

```bash
# Upload to multiple key servers
gpg --keyserver keys.openpgp.org --send-keys YOUR_KEY_ID
gpg --keyserver keyserver.ubuntu.com --send-keys YOUR_KEY_ID
gpg --keyserver pgp.mit.edu --send-keys YOUR_KEY_ID

# Verify upload
gpg --keyserver keys.openpgp.org --recv-keys YOUR_KEY_ID
```

### 2. Add to GitHub

```bash
# Export your public key
gpg --armor --export YOUR_KEY_ID

# Copy the output (including BEGIN and END lines)
```

Then:
1. Go to https://github.com/settings/keys
2. Click "New GPG key"
3. Paste your public key
4. Click "Add GPG key"

### 3. Host on Your Website

```bash
# Create a public key file
gpg --armor --export YOUR_KEY_ID > public-key.asc

# Upload to your website
# Example: https://yourdomain.com/pgp-key.asc
```

### 4. Add to Repository

```bash
# Add to your repository
mkdir -p docs/security
gpg --armor --export YOUR_KEY_ID > docs/security/pgp-public-key.asc

git add docs/security/pgp-public-key.asc
git commit -m "Add PGP public key for release verification"
git push
```

### 5. Update SECURITY.md

Update your `SECURITY.md` file:

```markdown
## PGP Key

**Key ID**: YOUR_KEY_ID
**Fingerprint**: YOUR_FINGERPRINT

### Public Key Locations

- **GitHub**: https://github.com/USERNAME.gpg
- **Key Server**: https://keys.openpgp.org/search?q=YOUR_KEY_ID
- **Repository**: [docs/security/pgp-public-key.asc](docs/security/pgp-public-key.asc)
- **Raw Key**: https://raw.githubusercontent.com/USERNAME/fastproxy/main/docs/security/pgp-public-key.asc

### Import Public Key

\`\`\`bash
# From key server
gpg --keyserver keys.openpgp.org --recv-keys YOUR_KEY_ID

# From file
curl https://raw.githubusercontent.com/USERNAME/fastproxy/main/docs/security/pgp-public-key.asc | gpg --import

# From GitHub
curl https://github.com/USERNAME.gpg | gpg --import
\`\`\`

### Verify Releases

\`\`\`bash
# Download release and signature
wget https://github.com/USERNAME/fastproxy/releases/download/v2.0.0/fastproxy-2.0.0.tar.gz
wget https://github.com/USERNAME/fastproxy/releases/download/v2.0.0/fastproxy-2.0.0.tar.gz.asc

# Verify signature
gpg --verify fastproxy-2.0.0.tar.gz.asc fastproxy-2.0.0.tar.gz
\`\`\`
```

## Backup Your Keys

### Export Private Key (KEEP SAFE!)

```bash
# Export private key (DANGEROUS - keep secure!)
gpg --armor --export-secret-keys YOUR_KEY_ID > private-key.asc

# IMPORTANT: Store this in a secure location!
# - Password manager
# - Encrypted USB drive
# - Hardware security key
# - Paper backup (yes, really!)
```

### Create a Revocation Certificate

```bash
# Create revocation certificate (in case key is compromised)
gpg --output revoke-certificate.asc --gen-revoke YOUR_KEY_ID

# Store this safely! You'll need it if your key is compromised.
```

### Secure Storage

```bash
# Create encrypted backup
tar -czf gpg-backup.tar.gz ~/.gnupg
gpg --symmetric --cipher-algo AES256 gpg-backup.tar.gz

# This creates: gpg-backup.tar.gz.gpg
# Store this encrypted file in multiple secure locations
```

## Complete Setup Script

Here's a complete script to set everything up:

```bash
#!/bin/bash

echo "🔐 FastProxy PGP Key Setup"
echo ""

# Check if GPG is installed
if ! command -v gpg &> /dev/null; then
    echo "❌ GPG is not installed"
    echo "Install with: brew install gnupg (macOS) or apt install gnupg (Linux)"
    exit 1
fi

echo "✅ GPG is installed"
echo ""

# Generate key
echo "📝 Generating PGP key..."
echo "Please follow the prompts:"
echo "  - Key type: 1 (RSA and RSA)"
echo "  - Key size: 4096"
echo "  - Expiration: 0 (does not expire) or 2y"
echo "  - Name: Your full name"
echo "  - Email: Your GitHub email"
echo ""

gpg --full-generate-key

# Get key ID
echo ""
echo "📋 Your keys:"
gpg --list-secret-keys --keyid-format=long

echo ""
echo "🔑 Copy your KEY_ID from above and enter it here:"
read -r KEY_ID

if [ -z "$KEY_ID" ]; then
    echo "❌ No KEY_ID provided"
    exit 1
fi

# Configure Git
echo ""
echo "⚙️  Configuring Git..."
git config --global user.signingkey "$KEY_ID"
git config --global commit.gpgsign true
git config --global tag.gpgsign true
git config --global gpg.program gpg

echo "✅ Git configured"

# Export public key
echo ""
echo "📤 Exporting public key..."
mkdir -p docs/security
gpg --armor --export "$KEY_ID" > docs/security/pgp-public-key.asc

echo "✅ Public key exported to: docs/security/pgp-public-key.asc"

# Upload to key server
echo ""
echo "☁️  Uploading to key servers..."
gpg --keyserver keys.openpgp.org --send-keys "$KEY_ID"
gpg --keyserver keyserver.ubuntu.com --send-keys "$KEY_ID"

echo "✅ Key uploaded to servers"

# Create backup
echo ""
echo "💾 Creating encrypted backup..."
gpg --output docs/security/revoke-certificate.asc --gen-revoke "$KEY_ID"

echo "✅ Revocation certificate created"

# Display public key for GitHub
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 PUBLIC KEY (Add to GitHub)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
cat docs/security/pgp-public-key.asc
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add public key to GitHub: https://github.com/settings/keys"
echo "2. Update SECURITY.md with your key ID"
echo "3. Commit the public key: git add docs/security && git commit -m 'Add PGP key'"
echo "4. Sign your next release: git tag -s v2.0.0 -m 'Release 2.0.0'"
echo ""
echo "🔐 Your key is ready!"
```

## Quick Reference

### Common Commands

```bash
# List keys
gpg --list-keys                    # Public keys
gpg --list-secret-keys            # Private keys

# Export keys
gpg --armor --export KEY_ID       # Export public key
gpg --armor --export-secret-keys KEY_ID  # Export private key (careful!)

# Sign commits
git commit -S -m "message"        # Sign single commit
git config --global commit.gpgsign true  # Auto-sign all commits

# Sign tags
git tag -s v1.0.0 -m "Release"    # Create signed tag
git tag -v v1.0.0                 # Verify signed tag

# Sign files
gpg --armor --detach-sign file.tar.gz    # Create signature
gpg --verify file.tar.gz.asc file.tar.gz # Verify signature

# Key management
gpg --edit-key KEY_ID             # Edit key
gpg --delete-key KEY_ID           # Delete public key
gpg --delete-secret-key KEY_ID    # Delete private key
```

## Troubleshooting

### GPG Agent Issues

```bash
# Restart GPG agent
gpgconf --kill gpg-agent
gpg-agent --daemon

# Or kill all GPG processes
killall gpg-agent
```

### Git Signing Issues

```bash
# Tell Git where GPG is
git config --global gpg.program $(which gpg)

# Or for macOS with GPG Suite
git config --global gpg.program /usr/local/bin/gpg

# Disable TTY if needed (for scripts)
export GPG_TTY=$(tty)
```

### Permission Issues

```bash
# Fix permissions
chmod 700 ~/.gnupg
chmod 600 ~/.gnupg/*
```

## Security Best Practices

1. ✅ **Use strong passphrase** - 20+ characters
2. ✅ **Backup private key** - Multiple secure locations
3. ✅ **Create revocation certificate** - Before you need it
4. ✅ **Set expiration** - Consider 2-5 year expiration
5. ✅ **Keep private key private** - Never share or commit
6. ✅ **Use key server** - Make public key easy to find
7. ✅ **Sign all releases** - Build trust with users
8. ✅ **Rotate periodically** - Update keys every few years

## Resources

- [GnuPG Documentation](https://gnupg.org/documentation/)
- [GitHub GPG Guide](https://docs.github.com/en/authentication/managing-commit-signature-verification)
- [Git Tools - Signing Your Work](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
- [Creating GPG Keys](https://keyring.debian.org/creating-key.html)

---

**🔐 Your releases are now cryptographically signed and verifiable!**

