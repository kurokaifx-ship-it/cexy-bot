import random,json,os
from telegram.ext import *

TOKEN="8988127615:AAEYrXG3iNBy8vqYY-MSHpGOxjzeCQ1O95g"

W={
4:["word","game","home","tree","book","time","love","star"],
5:["apple","house","water","green","world","hello","light","plant"],
6:["banana","orange","planet","silver","friend","school"],
7:["country","morning","picture","teacher","journey","freedom"]
}

G={}
R=json.load(open("cexy_rank.json")) if os.path.exists("cexy_rank.json") else {}

def save():json.dump(R,open("cexy_rank.json","w"))

def check(x,w):
    a=["⬜"]*len(w);q=list(w)
    for i in range(len(w)):
        if x[i]==w[i]:a[i]="🟩";q[i]=None
    for i in range(len(w)):
        if a[i]=="⬜" and x[i] in q:
            a[i]="🟨";q[q.index(x[i])]=None
    return " ".join(a)

async def game(u,c):
    n=int(u.message.text[-1]);ch=str(u.effective_chat.id)
    G[ch]={"w":random.choice(W[n]),"n":n,"t":[]}
    await u.message.reply_text(
        f"🎮 CEXY {n}\n\nGuess the {n}-letter word\n"
        f"Chance: 30\n\n🟩 Correct\n🟨 Wrong position\n⬜ Not found"
    )

async def guess(u,c):
    ch=str(u.effective_chat.id)
    if ch not in G:return
    x=u.message.text.lower().strip();g=G[ch];w,n=g["w"],g["n"]
    if len(x)!=n or not x.isalpha():return
    g["t"].append((x,check(x,w)))
    b="\n".join(f"{x.upper()}- {r}" for x,r in g["t"])
    await u.message.reply_text(f"🎮 CEXY {n} | {len(g['t'])}/30\n\n{b}")

    if x==w:
        uid=str(u.effective_user.id);R.setdefault(ch,{})
        R[ch].setdefault(uid,{"name":u.effective_user.first_name,"wins":0})
        R[ch][uid]["wins"]+=1;save()
        await u.message.reply_text(f"🎉 YOU WIN!\nWord: {w.upper()}")
        del G[ch]
    elif len(g["t"])>=30:
        await u.message.reply_text(f"❌ GAME OVER!\nWord: {w.upper()}")
        del G[ch]

async def rank(u,c):
    p=sorted(R.get(str(u.effective_chat.id),{}).values(),
             key=lambda x:x["wins"],reverse=True)
    s="\n".join(f"{i}. {x['name']} — {x['wins']} wins"
                for i,x in enumerate(p,1))
    await u.message.reply_text("🏆 CEXY RANKING\n\n"+(s or "No wins yet."))

async def admin(u,c,dem=False):
    m=await u.effective_chat.get_member(u.effective_user.id)
    if m.status not in ("administrator","creator"):
        return await u.message.reply_text("❌ Admin only.")

    r=u.message.reply_to_message
    if not r:
        return await u.message.reply_text("Reply to a member's message.")

    try:
        await u.effective_chat.promote_member(
            r.from_user.id,
            can_manage_chat=not dem,
            can_delete_messages=not dem,
            can_restrict_members=not dem,
            can_invite_users=not dem,
            can_pin_messages=not dem,
            can_change_info=not dem,
            can_manage_video_chats=not dem
        )
        await u.message.reply_text("✅ Done.")
    except Exception as e:
        await u.message.reply_text(f"❌ Failed: {e}")

app=Application.builder().token(TOKEN).build()

for n in (4,5,6,7):
    app.add_handler(CommandHandler(f"cexy{n}",game))

app.add_handler(CommandHandler("cexyrank",rank))
app.add_handler(CommandHandler("promote",admin))
app.add_handler(CommandHandler("demote",lambda u,c:admin(u,c,True)))
app.add_handler(MessageHandler(filters.TEXT&~filters.COMMAND,guess))

print("CEXY Bot Running...")
app.run_polling()
