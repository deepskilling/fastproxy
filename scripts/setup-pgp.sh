#!/bin/bash

# ============================================================================
# FastProxy PGP Key Setup Script
# ============================================================================
# This script helps you create and configure PGP keys for signing releases
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          FastProxy PGP Key Setup                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if GPG is installed
if ! command -v gpg &> /dev/null; then
    echo -e "${RED}❌ GPG is not installed${NC}"
    echo ""
    echo "Install GPG:"
    echo "  macOS:   brew install gnupg"
    echo "  Ubuntu:  sudo apt install gnupg"
    echo "  CentOS:  sudo yum install gnupg2"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ GPG is installed${NC}"
GPG_VERSION=$(gpg --version | head -n 1)
echo "   $GPG_VERSION"
echo ""

# Check if user already has keys
EXISTING_KEYS=$(gpg --list-secret-keys --keyid-format=long 2>/dev/null | grep -c "^sec" || echo "0")

if [ "$EXISTING_KEYS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  You already have $EXISTING_KEYS PGP key(s)${NC}"
    echo ""
    gpg --list-secret-keys --keyid-format=long
    echo ""
    read -p "Do you want to use an existing key? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🔑 Enter your KEY_ID from above (the part after rsa4096/):"
        read -r KEY_ID
        
        if [ -z "$KEY_ID" ]; then
            echo -e "${RED}❌ No KEY_ID provided${NC}"
            exit 1
        fi
        
        USE_EXISTING=true
    else
        USE_EXISTING=false
    fi
else
    USE_EXISTING=false
fi

# Generate new key if not using existing
if [ "$USE_EXISTING" = false ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📝 Generating New PGP Key"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Please provide the following information:"
    echo ""
    
    read -p "Full Name: " FULL_NAME
    read -p "Email (use your GitHub email): " EMAIL
    read -p "Comment (optional, e.g., 'FastProxy Release Signing'): " COMMENT
    
    echo ""
    echo "Recommended settings:"
    echo "  - Key type: 1 (RSA and RSA)"
    echo "  - Key size: 4096 (maximum security)"
    echo "  - Expiration: 0 (does not expire) or 2y (2 years)"
    echo ""
    
    # Generate key
    cat > /tmp/gpg-keygen-config <<EOF
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: $FULL_NAME
Name-Email: $EMAIL
EOF

    if [ -n "$COMMENT" ]; then
        echo "Name-Comment: $COMMENT" >> /tmp/gpg-keygen-config
    fi

    cat >> /tmp/gpg-keygen-config <<EOF
Expire-Date: 0
%ask-passphrase
%commit
EOF

    echo "Generating key... (this may take a moment)"
    gpg --batch --generate-key /tmp/gpg-keygen-config
    rm /tmp/gpg-keygen-config
    
    echo -e "${GREEN}✅ Key generated successfully${NC}"
    echo ""
    
    # Get the new key ID
    KEY_ID=$(gpg --list-secret-keys --keyid-format=long "$EMAIL" | grep "^sec" | sed 's/.*\/\([^ ]*\).*/\1/')
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  Configuring Git"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Configure Git
git config --global user.signingkey "$KEY_ID"
git config --global commit.gpgsign true
git config --global tag.gpgsign true
git config --global gpg.program gpg

# Set GPG_TTY for terminal
export GPG_TTY=$(tty)
echo "export GPG_TTY=\$(tty)" >> ~/.zshrc 2>/dev/null || echo "export GPG_TTY=\$(tty)" >> ~/.bashrc

echo -e "${GREEN}✅ Git configured to sign commits and tags${NC}"
echo ""

# Export public key
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📤 Exporting Public Key"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

mkdir -p "$REPO_ROOT/docs/security"
gpg --armor --export "$KEY_ID" > "$REPO_ROOT/docs/security/pgp-public-key.asc"

echo -e "${GREEN}✅ Public key exported to: docs/security/pgp-public-key.asc${NC}"
echo ""

# Get fingerprint
FINGERPRINT=$(gpg --fingerprint "$KEY_ID" | grep "Key fingerprint" | sed 's/.*= //')

echo "📋 Key Information:"
echo "   Key ID: $KEY_ID"
echo "   Fingerprint: $FINGERPRINT"
echo ""

# Upload to key servers
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "☁️  Uploading to Key Servers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

read -p "Upload public key to key servers? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    gpg --keyserver keys.openpgp.org --send-keys "$KEY_ID" 2>/dev/null || echo "Failed to upload to keys.openpgp.org"
    gpg --keyserver keyserver.ubuntu.com --send-keys "$KEY_ID" 2>/dev/null || echo "Failed to upload to keyserver.ubuntu.com"
    echo -e "${GREEN}✅ Key uploaded to servers${NC}"
else
    echo "⏭️  Skipped key server upload"
fi
echo ""

# Create revocation certificate
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔒 Creating Revocation Certificate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

gpg --output "$REPO_ROOT/docs/security/revoke-certificate.asc" --gen-revoke "$KEY_ID" <<EOF
y
0

y
EOF

echo -e "${GREEN}✅ Revocation certificate created${NC}"
echo -e "${YELLOW}⚠️  Store this safely! You'll need it if your key is compromised.${NC}"
echo ""

# Display public key
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 PUBLIC KEY (Add to GitHub)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
cat "$REPO_ROOT/docs/security/pgp-public-key.asc"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Update SECURITY.md
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Updating SECURITY.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Add PGP key info to SECURITY.md
if grep -q "PGP Key:" "$REPO_ROOT/SECURITY.md" 2>/dev/null; then
    # Replace existing PGP key section
    sed -i.bak "s|PGP Key: \[Link to PGP public key\]|PGP Key: [docs/security/pgp-public-key.asc](docs/security/pgp-public-key.asc)|g" "$REPO_ROOT/SECURITY.md"
    sed -i.bak "s|Key ID: .*|Key ID: $KEY_ID|g" "$REPO_ROOT/SECURITY.md"
    sed -i.bak "s|Fingerprint: .*|Fingerprint: $FINGERPRINT|g" "$REPO_ROOT/SECURITY.md"
    rm "$REPO_ROOT/SECURITY.md.bak" 2>/dev/null || true
    echo -e "${GREEN}✅ SECURITY.md updated${NC}"
else
    echo -e "${YELLOW}⚠️  Please manually update SECURITY.md with your key information${NC}"
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Setup Complete!                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🎉 Your PGP key is ready!${NC}"
echo ""
echo "📋 Key Information:"
echo "   Key ID: $KEY_ID"
echo "   Fingerprint: $FINGERPRINT"
echo "   Public Key: docs/security/pgp-public-key.asc"
echo ""
echo "Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 🔑 Add public key to GitHub:"
echo "   https://github.com/settings/keys"
echo ""
echo "2. 📝 Commit the public key:"
echo "   git add docs/security"
echo "   git commit -S -m 'Add PGP public key for release verification'"
echo "   git push"
echo ""
echo "3. 🏷️  Sign your next release:"
echo "   git tag -s v2.0.0 -m 'Release 2.0.0'"
echo "   git push origin v2.0.0"
echo ""
echo "4. 💾 Backup your private key (IMPORTANT!):"
echo "   gpg --armor --export-secret-keys $KEY_ID > private-key-backup.asc"
echo "   Store this file in a secure location!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 For more information, see: docs/guides/PGP_SETUP.md"
echo ""

