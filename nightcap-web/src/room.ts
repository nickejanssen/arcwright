export interface RoomMember {
  client_id: string;
  participant_id: string;
  character_id: string | null;
  role: "host" | "player" | "display";
  joined_at: string;
}

export interface RoomJoinRequest {
  session_id: string;
  client_id: string;
  participant_id: string;
  character_id?: string | null;
  role: RoomMember["role"];
}

export interface RoomSnapshot {
  session_id: string | null;
  room_id: string;
  member_count: number;
  members: RoomMember[];
  updated_at: string;
}

export interface RoomActionResponse {
  ok: true;
  snapshot: RoomSnapshot;
}

export interface NightcapRoomEnv {
  ARCWRIGHT_API_BASE_URL: string;
}

interface StoredRoomState {
  currentSessionId: string | null;
  members: RoomMember[];
}

export class NightcapRoom extends DurableObject {
  private readonly state: DurableObjectState;
  private readonly roomId: string;
  private currentSessionId: string | null = null;
  private readonly members = new Map<string, RoomMember>();
  private loadPromise: Promise<void> | null = null;

  constructor(state: DurableObjectState, env: NightcapRoomEnv) {
    super(state, env);
    this.state = state;
    this.roomId = state.id.toString();
  }

  async fetch(request: Request): Promise<Response> {
    await this.ensureLoaded();

    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname.endsWith("/snapshot")) {
      return this.json(this.snapshot());
    }

    if (request.method === "POST" && url.pathname.endsWith("/join")) {
      const body = await this.parseJoinRequest(request);
      if (!body) {
        return new Response("Invalid room join payload", { status: 400 });
      }

      return this.registerMember(body);
    }

    if (request.method === "POST" && url.pathname.endsWith("/leave")) {
      const body = await this.parseLeaveRequest(request);
      if (!body) {
        return new Response("Invalid room leave payload", { status: 400 });
      }

      return this.unregisterMember(body.client_id);
    }

    return new Response("Not found", { status: 404 });
  }

  private async ensureLoaded(): Promise<void> {
    if (!this.loadPromise) {
      this.loadPromise = (async () => {
        const stored =
          await this.state.storage.get<StoredRoomState>("room-state");
        if (!stored) {
          return;
        }

        this.currentSessionId = stored.currentSessionId;
        this.members.clear();
        for (const member of stored.members) {
          this.members.set(member.client_id, member);
        }
      })();
    }

    await this.loadPromise;
  }

  private async persist(): Promise<void> {
    await this.state.storage.put<StoredRoomState>("room-state", {
      currentSessionId: this.currentSessionId,
      members: [...this.members.values()],
    });
  }

  private async parseJoinRequest(
    request: Request,
  ): Promise<RoomJoinRequest | null> {
    let parsed: unknown;
    try {
      parsed = await request.json();
    } catch {
      return null;
    }

    if (!parsed || typeof parsed !== "object") {
      return null;
    }

    const candidate = parsed as Partial<RoomJoinRequest>;
    if (
      typeof candidate.session_id !== "string" ||
      candidate.session_id.length === 0 ||
      typeof candidate.client_id !== "string" ||
      candidate.client_id.length === 0 ||
      typeof candidate.participant_id !== "string" ||
      candidate.participant_id.length === 0 ||
      (candidate.character_id !== undefined &&
        candidate.character_id !== null &&
        typeof candidate.character_id !== "string") ||
      (candidate.role !== "host" &&
        candidate.role !== "player" &&
        candidate.role !== "display")
    ) {
      return null;
    }

    return candidate as RoomJoinRequest;
  }

  private async parseLeaveRequest(
    request: Request,
  ): Promise<Pick<RoomJoinRequest, "client_id"> | null> {
    let parsed: unknown;
    try {
      parsed = await request.json();
    } catch {
      return null;
    }

    if (!parsed || typeof parsed !== "object") {
      return null;
    }

    const candidate = parsed as Partial<RoomJoinRequest>;
    if (
      typeof candidate.client_id !== "string" ||
      candidate.client_id.length === 0
    ) {
      return null;
    }

    return { client_id: candidate.client_id };
  }

  private async registerMember(body: RoomJoinRequest): Promise<Response> {
    if (this.currentSessionId && this.currentSessionId !== body.session_id) {
      return new Response("Room already bound to another session", {
        status: 409,
      });
    }

    this.currentSessionId = body.session_id;
    this.members.set(body.client_id, {
      client_id: body.client_id,
      participant_id: body.participant_id,
      character_id: body.character_id ?? null,
      role: body.role,
      joined_at: new Date().toISOString(),
    });
    await this.persist();

    return this.json({
      ok: true,
      snapshot: this.snapshot(),
    });
  }

  private async unregisterMember(clientId: string): Promise<Response> {
    this.members.delete(clientId);
    if (this.members.size === 0) {
      this.currentSessionId = null;
    }
    await this.persist();

    return this.json({
      ok: true,
      snapshot: this.snapshot(),
    });
  }

  private snapshot(): RoomSnapshot {
    return {
      session_id: this.currentSessionId,
      room_id: this.roomId,
      member_count: this.members.size,
      members: [...this.members.values()],
      updated_at: new Date().toISOString(),
    };
  }

  private json(value: RoomSnapshot | RoomActionResponse): Response {
    return new Response(JSON.stringify(value), {
      headers: {
        "content-type": "application/json; charset=utf-8",
      },
    });
  }
}
