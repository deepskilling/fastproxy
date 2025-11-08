#!/bin/bash

# Simple PGP Key Setup for FastProxy

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          FastProxy PGP Key Setup                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "✅ GPG is installed: $(gpg --version | head -n 1)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Generating PGP Key"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will create a 4096-bit RSA key for signing your FastProxy releases."
echo ""
echo "You will be asked for:"
echo "  1. Full Name"
echo "  2. Email (use your GitHub email)"
echo "  3. Comment (optional)"
echo "  4. Passphrase (IMPORTANT - remember this!)"
echo ""
echo "Press Enter to continue..."
read

# Run GPG key generation
gpg --full-generate-key

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Your Keys:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gpg --list-secret-keys --keyid-format=long
echo ""

echo "Enter your KEY_ID from above (the part after 'rsa4096/'):"
read -r KEY_ID

if [ -z "$KEY_ID" ]; then
    echo "❌ No KEY_ID provided. Exiting."
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  Configuring Git"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

git config --global user.signingkey "$KEY_ID"
git config --global commit.gpgsign true
git config --global tag.gpgsign true
git config --global gpg.program gpg

echo "✅ Git configured to sign all commits and tags"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📤 Exporting Public Key"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p "$REPO_ROOT/docs/security"
gpg --armor --export "$KEY_ID" > "$REPO_ROOT/docs/security/pgp-public-key.asc"

echo "✅ Public key exported to: docs/security/pgp-public-key.asc"
echo ""

FINGERPRINT=$(gpg --fingerprint "$KEY_ID" | grep "Key fingerprint" | sed 's/.*= //')

echo "📋 Key Information:"
echo "   Key ID: $KEY_ID"
echo "   Fingerprint: $FINGERPRINT"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "☁️  Upload to Key Servers? (Y/n)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -r UPLOAD

if [ "$UPLOAD" != "n" ] && [ "$UPLOAD" != "N" ]; then
    echo "Uploading to key servers..."
    gpg --keyserver keys.openpgp.org --send-keys "$KEY_ID" 2>&1 | head -5
    gpg --keyserver keyserver.ubuntu.com --send-keys "$KEY_ID" 2>&1 | head -5
    echo "✅ Key uploaded"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 YOUR PUBLIC KEY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "$REPO_ROOT/docs/security/pgp-public-key.asc"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Setup Complete!                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 Your PGP key is ready!"
echo ""
echo "Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Add public key to GitHub:"
echo "   https://github.com/settings/keys"
echo "   Copy the key shown above (including BEGIN/END lines)"
echo ""
echo "2. Update SECURITY.md with your key info:"
echo "   Key ID: $KEY_ID"
echo "   Fingerprint: $FINGERPRINT"
echo ""
echo "3. Commit the public key:"
echo "   git add docs/security"
echo "   git commit -S -m 'Add PGP public key'"
echo "   git push"
echo ""
echo "4. Sign your next release:"
echo "   git tag -s v2.0.0 -m 'Release 2.0.0'"
echo "   git push origin v2.0.0"
echo ""
echo "📚 See docs/guides/PGP_SETUP.md for more information"
echo ""

