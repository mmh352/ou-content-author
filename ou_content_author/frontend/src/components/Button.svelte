<script lang="ts">
    import { createEventDispatcher } from 'svelte';

    export let type = 'button';
    export let ariaLabel = null;
    export let style = 'default';

    const dispatch = createEventDispatcher();

    function handleClick(ev) {
        dispatch('action', ev);
    }
</script>

<button on:click={handleClick} type={type} aria-label={ariaLabel} class="block px-1 py-1 border {style === 'success' ? 'border-green text-green hover:bg-green hover:text-white focus:bg-green focus:text-white' : (style === 'failure' ? 'border-red text-red hover:bg-red hover:text-white focus:bg-red focus:text-white' : (style === 'secondary' ? 'border-gray-900 text-gray-900 hover:bg-gray-900 hover:text-white focus:bg-gray-900 focus:text-white' : 'border-blue text-blue hover:bg-blue hover:text-white focus:bg-blue focus:text-white'))} transition-colors"><slot></slot></button>
