<script lang="ts">

</script>

<div class="fixed left-0 top-0 w-screen h-screen bg-white/75 z-50">
    <div role="dialog" class="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col bg-white border-2 border-blue shadow-xl" aria-modal="true">
        {#if $$slots.title}
            <div class="flex-0 bg-blue text-white text-xl px-2 py-1"><slot name="title"></slot></div>
        {/if}
        {#if $$slots.content}
            <div class="flex-auto px-2 py-1"><slot name="content"></slot></div>
        {/if}
        {#if $$slots.buttons}
            <div class="flex-0 px-2 pt-3 pb-1"><slot name="buttons"></slot></div>
        {/if}
    </div>
</div>
