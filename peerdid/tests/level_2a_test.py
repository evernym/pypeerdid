# Software that supports Level 2a of the peer DID spec is able to accept static DID docs
# from another party, and to correctly resolve and validate them. These features are
# almost directly observable in our peerdid library -- "almost" because some of them
# require an application layer to be fully exercised. We will therefore construct an
# extremely simple application layer to fill that role. It just maintains a repo in a
# folder, so we can depend on data being in a particular location when we have to do
# things like resolve.