<script lang="ts">
	import { onMount } from 'svelte';

	import GitInteraction from './components/GitInteraction.svelte';
	import FileTree from './components/FileTree.svelte';
	import FileEditor from './components/FileEditor.svelte';
	import PageViewer from './components/PageViewer.svelte';
	import ModalDialog from './components/ModalDialog.svelte';
	import Button from './components/Button.svelte';

	import { connect, isInitialising, isReady, isDisconnected } from './store';

	onMount(() => {
		connect();
	});
</script>

<main class="v-screen h-screen flex flex-col">
	<h1 class="sr-only">OU Content Author</h1>
	{#if $isInitialising}
		<ModalDialog>
			<h2 slot="title">Connecting...</h2>
			<div slot="content">
				<p>The connection to the server is being set up. Please wait...</p>
			</div>
		</ModalDialog>
	{:else if $isReady}
	<GitInteraction/>
	<div class="flex-auto flex flex-row">
		<FileTree/>
		<FileEditor/>
		<PageViewer/>
	</div>
	{:else if $isDisconnected}
		<ModalDialog>
			<h2 slot="title">Disconnected</h2>
			<div slot="content">
				<p>The connection to the server has closed.</p>
			</div>
			<ul slot="buttons" class="flex flex-row justify-end">
				<li><Button on:action={() => { window.location.reload(); }}>Reconnect</Button></li>
			</ul>
		</ModalDialog>
	{/if}
</main>

<style global>
	@tailwind base;
	@tailwind components;
	@tailwind utilities;

	.cmt-heading {
		@apply font-bold;
	}

	#page-viewer h1 {
		@apply text-xl mb-2 text-blue-800;
	}

	#page-viewer h2 {
		@apply text-lg mb-2 text-blue-800;
	}

	#page-viewer p {
		@apply mb-2;
	}
</style>
