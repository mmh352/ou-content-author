/// <reference types="svelte" />

type Message = CloneRepositoryMessage |
               RepositoryMessage |
               DeleteRepositoryMessage |
               RepositoryDeletedMessage |
               CheckoutBranchMessage |
               BranchMessage |
               SelectBlockMessage |
               BlockMessage |
               LoadFileContentMessage |
               FileContentMessage |
               SaveFileContentMessage |
               FileRenderingMessage |
               FileRenderedMessage |
               CommitChangesMessage |
               DiscardChangesMessage |
               ChangesCommittedMessage |
               ChangesDiscardedMessage |
               ChangesFoundMessage |
               NoChangesFoundMessage |
               AddFileMessage |
               DeleteFileMessage;

type CloneRepositoryMessage = {
    type: 'clone-repository',
    url: string,
};

type RepositoryMessage = {
    type: 'repository',
    branches: string[],
};

type DeleteRepositoryMessage = {
    type: 'delete-repository',
};

type RepositoryDeletedMessage = {
    type: 'repository-deleted',
};

type CheckoutBranchMessage = {
    type: 'checkout-branch',
    branch: string,
};

type BranchMessage = {
    type: 'branch',
    blocks: string[],
};

type SelectBlockMessage = {
    type: 'select-block',
    block: string,
};

type BlockMessage = {
    type: 'block',
    path: string,
    files: BlockFile[],
};

type BlockFile = {
    directory: string;
    filename: string;
};

type LoadFileContentMessage = {
    type: 'load-file-content',
    block: string,
    file: BlockFile,
};

type FileContentMessage = {
    type: 'file-content',
    content: string,
};

type SaveFileContentMessage = {
    type: 'save-file-content',
    block: string,
    file: BlockFile,
    content: string,
};

type FileRenderingMessage = {
    type: 'file-rendering',
};

type FileRenderedMessage = {
    type: 'file-rendered',
    url: string,
    output: string;
};

type CommitChangesMessage = {
    type: 'commit-changes',
    name: string,
    email: string,
    message: string,
};

type DiscardChangesMessage = {
    type: 'discard-changes',
};

type ChangesCommittedMessage = {
    type: 'changes-committed',
};

type ChangesDiscardedMessage = {
    type: 'changes-discarded',
};

type ChangesFoundMessage = {
    type: 'changes-found',
};

type NoChangesFoundMessage = {
    type: 'no-changes-found',
};

type AddFileMessageMessage = {
    type: 'add-file',
    block: string,
    file: BlockFile,
};

type DeleteFileMessageMessage = {
    type: 'delete-file',
    block: string,
    file: BlockFile,
};
